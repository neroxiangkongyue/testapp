# api/endpoints/word.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.word import WordCreate, WordRead, WordUpdate
from app.crud.word import (
    create_word, get_word, get_words, update_word,
    delete_word, search_words, get_word_by_normalized, get_by_word
)

router = APIRouter(prefix="/words", tags=["words"])


@router.post("/", response_model=WordRead)
def create_word_endpoint(word: WordCreate, db: Session = Depends(get_db)):
    """创建新单词"""
    # 检查标准化单词是否已存在
    word.normalized_word = word.word.lower()
    existing_word = get_word_by_normalized(db, word.normalized_word)
    if existing_word:
        raise HTTPException(status_code=400, detail="单词已存在")

    return create_word(db, word)


@router.get("/", response_model=List[WordRead])
def read_words_endpoint(
        skip: int = 0,
        limit: int = 100,
        is_common: Optional[bool] = None,
        difficulty_level_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """获取单词列表"""
    return get_words(
        db,
        skip=skip,
        limit=limit,
        is_common=is_common,
        difficulty_level_id=difficulty_level_id
    )


@router.get("/{word_id}", response_model=WordRead)
def read_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """根据ID获取单词"""
    word = get_word(db, word_id)
    if not word:
        raise HTTPException(status_code=404, detail="单词未找到")
    return word


@router.get("/search/{query}", response_model=List[WordRead])
def search_words_endpoint(query: str, limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """搜索单词"""
    return search_words(db, query, limit)


@router.put("/{word_id}", response_model=WordRead)
def update_word_endpoint(word_id: int, word_update: WordUpdate, db: Session = Depends(get_db)):
    """更新单词"""
    word = update_word(db, word_id, word_update)
    if not word:
        raise HTTPException(status_code=404, detail="单词未找到或单词已存在但id不同")
    return word


@router.delete("/{word_id}")
def delete_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """删除单词"""
    success = delete_word(db, word_id)
    if not success:
        raise HTTPException(status_code=404, detail="单词未找到")
    return {"message": "单词已删除"}


# api/endpoints/word.py (新增内容)
@router.put("/by-word/{word_text}", response_model=WordRead)
def update_word_by_text(
        word_text: str,
        word_update: WordUpdate,
        db: Session = Depends(get_db)
):
    """通过单词文本更新单词"""
    # 首先查找单词
    word = get_by_word(db, word_text)

    if not word:
        raise HTTPException(status_code=404, detail="单词未找到")
    return update_word(db, word.id, word_update)


@router.delete("/by-word/{word_text}")
def delete_word_by_text(word_text: str, db: Session = Depends(get_db)):
    """通过单词文本删除单词"""
    # 首先查找单词
    word = get_by_word(db, word_text)

    if not word:
        raise HTTPException(status_code=404, detail="单词未找到")

    success = delete_word(db, word.id)
    if not success:
        raise HTTPException(status_code=404, detail="单词未找到")

    return {"message": "单词已删除"}


# api/endpoints/word.py (新增内容)
@router.get("/by-word/{word_text}", response_model=WordRead)
def update_word_by_text(
        word_text: str,
        db: Session = Depends(get_db)
):
    """通过单词文本查找单词"""
    # 首先查找单词
    word = get_by_word(db, word_text)

    if not word:
        raise HTTPException(status_code=404, detail="单词未找到")

    return word
