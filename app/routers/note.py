from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, Note, NoteWithRelations, NoteBrief, WordBrief, RelationBrief, \
    UserBrief
from app.crud.note import (
    create_note, get_note, get_note_with_visibility_check, get_notes,
    get_user_notes, get_collected_notes, update_note,
    delete_note, increment_note_views, collect_note, uncollect_note,
    check_note_collected, get_note_words, get_note_relations,
    get_notes_by_word_id, get_notes_by_relation_id, search_notes, toggle_note_like
)
from app.crud.word import get_word
from app.crud.relation import get_relation

notes_router = APIRouter(prefix="/notes", tags=["notes"])


@notes_router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_new_note(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        note_in: NoteCreate
):
    """创建新笔记"""
    # 验证关联的单词和关系是否存在
    word_ids = note_in.word_ids or []
    relation_ids = note_in.relation_ids or []

    for word_id in word_ids:
        word = get_word(db, word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word ID {word_id} not found"
            )

    for relation_id in relation_ids:
        relation = get_relation(db, relation_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relation ID {relation_id} not found"
            )

    # 创建笔记
    note = create_note(
        db, note_in, current_user.id, word_ids, relation_ids
    )
    return note


@notes_router.get("/", response_model=List[NoteBrief])
def read_notes(
        db: Session = Depends(get_db),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        keyword: Optional[str] = None,
        current_user: Optional[User] = Depends(get_current_user)
):
    """获取笔记列表（考虑可见性）"""
    user_id = current_user.id if current_user else None
    notes = get_notes(db, skip=skip, limit=limit, user_id=user_id, keyword=keyword)
    return notes


@notes_router.get("/my-notes", response_model=List[NoteBrief])
def read_my_notes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
):
    """获取当前用户创建的笔记"""
    notes = get_user_notes(db, current_user.id, skip=skip, limit=limit)
    return notes


@notes_router.get("/collected", response_model=List[NoteBrief])
def read_collected_notes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
):
    """获取当前用户收藏的笔记"""
    notes = get_collected_notes(db, current_user.id, skip=skip, limit=limit)
    return notes


@notes_router.get("/word/{word_id}", response_model=List[NoteBrief])
def read_notes_by_word(
        *,
        db: Session = Depends(get_db),
        word_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: Optional[User] = Depends(get_current_user)
):
    """通过单词ID获取相关笔记"""
    user_id = current_user.id if current_user else None
    notes = get_notes_by_word_id(db, word_id, user_id, skip=skip, limit=limit)
    return notes


@notes_router.get("/relation/{relation_id}", response_model=List[NoteBrief])
def read_notes_by_relation(
        *,
        db: Session = Depends(get_db),
        relation_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: Optional[User] = Depends(get_current_user)
):
    """通过关系ID获取相关笔记"""
    user_id = current_user.id if current_user else None
    notes = get_notes_by_relation_id(db, relation_id, user_id, skip=skip, limit=limit)
    return notes


@notes_router.get("/search", response_model=List[NoteBrief])
def search_notes_by_keyword(
        *,
        db: Session = Depends(get_db),
        keyword: str = Query(..., min_length=1),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: Optional[User] = Depends(get_current_user)
):
    """搜索笔记"""
    user_id = current_user.id if current_user else None
    notes = search_notes(db, keyword, user_id, skip=skip, limit=limit)
    return notes


@notes_router.get("/{note_id}", response_model=NoteWithRelations)
def read_note(
        *,
        db: Session = Depends(get_db),
        note_id: int,
        current_user: Optional[User] = Depends(get_current_user)
):
    """获取笔记详情（考虑可见性）"""
    user_id = current_user.id if current_user else None
    note = get_note_with_visibility_check(db, note_id, user_id)

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or access denied"
        )

    # 增加浏览量
    note = increment_note_views(db, note)

    # 获取关联的单词和关系
    word_ids = get_note_words(db, note_id)
    relation_ids = get_note_relations(db, note_id)

    # 获取单词和关系的详细信息
    words = []
    for word_id in word_ids:
        word = get_word(db, word_id)
        if word:
            words.append(WordBrief(
                id=word.id,
                word=word.word,
                normalized_word=word.normalized_word,
                length=word.length
            ))

    relations = []
    for relation_id in relation_ids:
        relation = get_relation(db, relation_id)
        if relation:
            relations.append(RelationBrief(
                id=relation.id,
                description=relation.description,
                strength=relation.strength
            ))

    # 检查当前用户是否收藏
    is_collected = False
    if current_user:
        is_collected = check_note_collected(db, note_id, current_user.id)

    # 构建响应
    note_response = NoteWithRelations(
        **note.dict(),
        words=words,
        relations=relations,
        creator=UserBrief(
            id=note.creator_rel.id,
            username=note.creator_rel.username,
            avatar_url=note.creator_rel.avatar_url
        ),
        is_collected=is_collected
    )

    return note_response


@notes_router.put("/{note_id}", response_model=Note)
def update_note_details(
        *,
        db: Session = Depends(get_db),
        note_id: int,
        note_in: NoteUpdate,
        current_user: User = Depends(get_current_user)
):
    """更新笔记"""
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    if note.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this note"
        )

    note = update_note(db, note, note_in)
    return note


@notes_router.delete("/{note_id}")
def delete_note_by_id(
        *,
        db: Session = Depends(get_db),
        note_id: int,
        current_user: User = Depends(get_current_user)
):
    """删除笔记"""
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    if note.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this note"
        )

    success = delete_note(db, note)
    if success:
        return {"message": "Note deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed"
        )


@notes_router.post("/{note_id}/collect")
def collect_note_by_id(
        *,
        db: Session = Depends(get_db),
        note_id: int,
        current_user: User = Depends(get_current_user)
):
    """收藏笔记"""
    success = collect_note(db, note_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot collect this note (already collected or note is not public)"
        )

    return {"message": "Note collected successfully"}


@notes_router.delete("/{note_id}/collect")
def uncollect_note_by_id(
        *,
        db: Session = Depends(get_db),
        note_id: int,
        current_user: User = Depends(get_current_user)
):
    """取消收藏笔记"""
    success = uncollect_note(db, note_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note not collected"
        )

    return {"message": "Note uncollected successfully"}


@notes_router.post("/{note_id}/like")
def like_note_by_id(
        *,
        db: Session = Depends(get_db),
        note_id: int,
        current_user: User = Depends(get_current_user)
):
    """点赞笔记"""
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    note = toggle_note_like(db, note)
    return {"likes": note.likes, "message": "Note liked successfully"}


@notes_router.post("/{note_id}/share")
def share_note_by_id(
        *,
        db: Session = Depends(get_db),
        note_id: int,
        current_user: User = Depends(get_current_user)
):
    """分享笔记"""
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # 增加分享次数
    note.shares += 1
    db.add(note)
    db.commit()
    db.refresh(note)

    return {"shares": note.shares, "message": "Note shared successfully"}
