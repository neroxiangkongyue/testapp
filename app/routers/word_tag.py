# app/routers/word_tag.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.word import TagUpdate, WordRead, TagCreate
from app.schemas.word_relation import TagRead
from app.crud.word_relation import (
    get_word_tags, add_tag_to_word, remove_tag_from_word,
    get_word_id_by_text, is_exist_tag_relation, get_tag_by_name, get_all_tags, get_tag_by_id, update_tag,
    delete_tag, get_words_by_tag, get_words_by_tag_name, create_tag_by_dict
)

word_tag_router = APIRouter(prefix="/words/{word_text}/tags", tags=["word tags"])


@word_tag_router.get("/", response_model=List[TagRead])
def read_word_tags(word_text: str, db: Session = Depends(get_db)):
    """获取单词的所有标签"""
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    tags = get_word_tags(db, word_id)
    return tags


@word_tag_router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def add_tag(
        word_text: str,
        tag: TagCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """为单词添加标签"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    # 检查标签是否已存在
    if is_exist_tag_relation(db, word_id, tag.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists for this word"
        )

    db_tag = add_tag_to_word(db, word_id, tag.name, tag.type)
    return db_tag


@word_tag_router.delete("/{tag_name}")
def remove_tag(
        word_text: str,
        tag_name: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """从单词移除标签"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 检查标签是否存在
    tag = get_tag_by_name(db, tag_name)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # 检查标签关联是否存在
    if not is_exist_tag_relation(db, word_id, tag_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not associated with this word"
        )

    success = remove_tag_from_word(db, word_id, tag_name)
    if success:
        return {"message": "Tag removed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Remove failed"
        )


@word_tag_router.get("/", response_model=List[TagRead])
def read_tags(
        skip: int = Query(0, ge=0, description="跳过数量"),
        limit: int = Query(100, ge=1, le=1000, description="返回数量"),
        db: Session = Depends(get_db)
):
    """获取所有标签"""
    tags = get_all_tags(db, skip=skip, limit=limit)
    return tags


@word_tag_router.get("/{tag_id}", response_model=TagRead)
def read_tag_by_id(tag_id: int, db: Session = Depends(get_db)):
    """通过ID获取标签"""
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@word_tag_router.get("/name/{tag_name}", response_model=TagRead)
def read_tag_by_name(tag_name: str, db: Session = Depends(get_db)):
    """通过名称获取标签"""
    tag = get_tag_by_name(db, tag_name)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@word_tag_router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_new_tag(
        tag: TagCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """创建新标签"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    try:
        db_tag = create_tag_by_dict(db, tag.dict())
        return db_tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@word_tag_router.put("/{tag_id}", response_model=TagRead)
def update_existing_tag(
        tag_id: int,
        tag_update: TagUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新标签"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    try:
        update_data = tag_update.dict(exclude_unset=True)
        db_tag = update_tag(db, tag_id, update_data)
        return db_tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@word_tag_router.delete("/{tag_id}")
def delete_existing_tag(
        tag_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """删除标签"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    success = delete_tag(db, tag_id)
    if success:
        return {"message": "Tag deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed"
        )


@word_tag_router.get("/{tag_id}/words", response_model=List[WordRead])
def read_words_by_tag_id(tag_id: int, db: Session = Depends(get_db)):
    """获取拥有指定标签的所有单词"""
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    words = get_words_by_tag(db, tag_id)
    return words


@word_tag_router.get("/name/{tag_name}/words", response_model=List[WordRead])
def read_words_by_tag_name(tag_name: str, db: Session = Depends(get_db)):
    """通过标签名获取所有相关单词"""
    tag = get_tag_by_name(db, tag_name)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    words = get_words_by_tag_name(db, tag_name)
    return words
