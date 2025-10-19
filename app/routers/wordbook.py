from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.user import get_user_by_id
from app.crud.word import get_word
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.book import (
    WordbookCreate, WordbookUpdate, Wordbook, WordbookBrief, WordbookWithWords,
    WordbookWordLinkCreate, WordBrief, UserBrief
)
from app.crud.book import (
    create_wordbook, get_wordbook, get_wordbook_with_visibility_check, get_wordbooks,
    get_user_wordbooks, get_collected_wordbooks, update_wordbook, delete_wordbook,
    add_word_to_wordbook, remove_word_from_wordbook, get_wordbook_words,
    collect_wordbook, uncollect_wordbook, check_wordbook_collected
)


wordbooks_router = APIRouter(prefix="/wordbooks", tags=["wordbooks"])


@wordbooks_router.post("/", response_model=Wordbook, status_code=status.HTTP_201_CREATED)
def create_new_wordbook(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    wordbook_in: WordbookCreate
):
    """创建新词库"""
    wordbook = create_wordbook(db, wordbook_in, current_user.id)
    return wordbook


@wordbooks_router.get("/", response_model=List[WordbookBrief])
def read_wordbooks(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_public: Optional[bool] = None,
    keyword: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取词库列表（考虑可见性）"""
    user_id = current_user.id if current_user else None
    wordbooks = get_wordbooks(db, skip=skip, limit=limit, user_id=user_id, is_public=is_public, keyword=keyword)
    return wordbooks


@wordbooks_router.get("/my-wordbooks", response_model=List[WordbookBrief])
def read_my_wordbooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """获取当前用户创建的词库"""
    wordbooks = get_user_wordbooks(db, current_user.id, skip=skip, limit=limit)
    return wordbooks


@wordbooks_router.get("/collected", response_model=List[WordbookBrief])
def read_collected_wordbooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """获取当前用户收藏的词库"""
    wordbooks = get_collected_wordbooks(db, current_user.id, skip=skip, limit=limit)
    return wordbooks


@wordbooks_router.get("/{wordbook_id}", response_model=WordbookWithWords)
def read_wordbook(
    *,
    db: Session = Depends(get_db),
    wordbook_id: int,
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取词库详情（考虑可见性）"""
    user_id = current_user.id if current_user else None
    wordbook = get_wordbook_with_visibility_check(db, wordbook_id, user_id)

    if not wordbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wordbook not found or access denied"
        )

    # 获取关联的单词
    word_ids = get_wordbook_words(db, wordbook_id)
    words = []
    for word_id in word_ids:
        word = get_word(db, word_id)
        if word:
            words.append(WordBrief.from_orm(word))

    # 获取创建者信息
    creator = get_user_by_id(db, wordbook.creator_id)

    # 检查当前用户是否收藏
    is_collected = False
    if current_user:
        is_collected = check_wordbook_collected(db, wordbook_id, current_user.id)

    # 构建响应
    wordbook_response = WordbookWithWords(
        **wordbook.dict(),
        words=words,
        creator=UserBrief.from_orm(creator) if creator else None,
        is_collected=is_collected
    )

    return wordbook_response


@wordbooks_router.put("/{wordbook_id}", response_model=Wordbook)
def update_wordbook_details(
    *,
    db: Session = Depends(get_db),
    wordbook_id: int,
    wordbook_in: WordbookUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新词库"""
    wordbook = get_wordbook(db, wordbook_id)
    if not wordbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wordbook not found"
        )

    if wordbook.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this wordbook"
        )

    wordbook = update_wordbook(db, wordbook, wordbook_in)
    return wordbook


@wordbooks_router.delete("/{wordbook_id}")
def delete_wordbook_by_id(
    *,
    db: Session = Depends(get_db),
    wordbook_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除词库"""
    wordbook = get_wordbook(db, wordbook_id)
    if not wordbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wordbook not found"
        )

    if wordbook.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this wordbook"
        )

    success = delete_wordbook(db, wordbook)
    if success:
        return {"message": "Wordbook deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed"
        )


@wordbooks_router.post("/{wordbook_id}/words")
def add_word_to_wordbook_route(
    *,
    db: Session = Depends(get_db),
    wordbook_id: int,
    word_link_in: WordbookWordLinkCreate,
    current_user: User = Depends(get_current_user)
):
    """添加单词到词库"""
    wordbook = get_wordbook(db, wordbook_id)
    if not wordbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wordbook not found"
        )

    if wordbook.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this wordbook"
        )

    success = add_word_to_wordbook(db, wordbook_id, word_link_in.word_id, word_link_in.order, word_link_in.note)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add word to wordbook (word not found or already exists)"
        )

    return {"message": "Word added to wordbook successfully"}


@wordbooks_router.delete("/{wordbook_id}/words/{word_id}")
def remove_word_from_wordbook_route(
    *,
    db: Session = Depends(get_db),
    wordbook_id: int,
    word_id: int,
    current_user: User = Depends(get_current_user)
):
    """从词库移除单词"""
    wordbook = get_wordbook(db, wordbook_id)
    if not wordbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wordbook not found"
        )

    if wordbook.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this wordbook"
        )

    success = remove_word_from_wordbook(db, wordbook_id, word_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word not found in wordbook"
        )

    return {"message": "Word removed from wordbook successfully"}


@wordbooks_router.post("/{wordbook_id}/collect")
def collect_wordbook_by_id(
    *,
    db: Session = Depends(get_db),
    wordbook_id: int,
    current_user: User = Depends(get_current_user)
):
    """收藏词库"""
    success = collect_wordbook(db, wordbook_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot collect this wordbook (already collected or wordbook is not public)"
        )

    return {"message": "Wordbook collected successfully"}


@wordbooks_router.delete("/{wordbook_id}/collect")
def uncollect_wordbook_by_id(
    *,
    db: Session = Depends(get_db),
    wordbook_id: int,
    current_user: User = Depends(get_current_user)
):
    """取消收藏词库"""
    success = uncollect_wordbook(db, wordbook_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wordbook not collected"
        )

    return {"message": "Wordbook uncollected successfully"}
