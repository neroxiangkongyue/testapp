# app/routers/word_pronunciations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.word_relation import WordPronunciationCreate, WordPronunciationRead, WordPronunciationUpdate
from app.crud.word_relation import (
    get_word_pronunciations, get_pronunciation_by_id, create_word_pronunciation,
    update_word_pronunciation, delete_word_pronunciation, is_exist_pronunciation, get_word_id_by_text
)

word_pronunciation_router = APIRouter(prefix="/words/{word_text}/pronunciations", tags=["word pronunciations"])


@word_pronunciation_router.get("/", response_model=List[WordPronunciationRead])
def read_word_pronunciations(word_text: str, db: Session = Depends(get_db)):
    """获取单词的所有发音"""
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    pronunciations = get_word_pronunciations(db, word_id)
    return pronunciations


@word_pronunciation_router.get("/{pronunciation_id}", response_model=WordPronunciationRead)
def read_word_pronunciation_by_id(pronunciation_id: int, db: Session = Depends(get_db)):
    """通过发音id获取单词的发音"""
    pronunciation = get_pronunciation_by_id(db, pronunciation_id)
    if not pronunciation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pronunciation not found"
        )
    return pronunciation


@word_pronunciation_router.post("/", response_model=WordPronunciationRead, status_code=status.HTTP_201_CREATED)
def create_pronunciation(
        word_text: str,
        pronunciation: WordPronunciationCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """为单词创建新发音"""
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

    db_pronunciation = create_word_pronunciation(db, word_id, pronunciation.dict())
    return db_pronunciation


@word_pronunciation_router.put("/{pronunciation_id}", response_model=WordPronunciationRead)
def update_pronunciation(
        word_text: str,
        pronunciation_id: int,
        pronunciation_update: WordPronunciationUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新单词的发音"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    # 验证单词存在
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 验证发音存在且属于该单词
    exist_pronunciation = is_exist_pronunciation(db, pronunciation_id, word_id)
    if not exist_pronunciation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pronunciation not found"
        )

    # 更新发音
    update_data = pronunciation_update.dict(exclude_unset=True)
    db_pronunciation = update_word_pronunciation(db, pronunciation_id, update_data)
    return db_pronunciation


@word_pronunciation_router.delete("/{pronunciation_id}")
def delete_pronunciation(
        word_text: str,
        pronunciation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """安全删除单词的指定发音"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    # 验证单词存在
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 验证发音存在且属于该单词
    exist_pronunciation = is_exist_pronunciation(db, pronunciation_id, word_id)
    if not exist_pronunciation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pronunciation not found"
        )

    # 执行删除
    is_delete_pronunciation = delete_word_pronunciation(db, pronunciation_id)
    if is_delete_pronunciation:
        return {"message": "Pronunciation deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed"
        )