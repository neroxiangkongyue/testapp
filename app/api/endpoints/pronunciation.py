# api/endpoints/pronunciation.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_db
from app.schemas.word import WordPronunciationCreate, WordPronunciationRead, WordPronunciationUpdate
from app.crud.pronunciation import (
    create_pronunciation, get_pronunciation, get_pronunciations_by_word,
    update_pronunciation, delete_pronunciation
)

router = APIRouter(prefix="/pronunciations", tags=["pronunciations"])

@router.post("/", response_model=WordPronunciationRead)
def create_pronunciation_endpoint(pronunciation: WordPronunciationCreate, db: Session = Depends(get_db)):
    """创建新发音"""
    return create_pronunciation(db, pronunciation)

@router.get("/word/{word_id}", response_model=List[WordPronunciationRead])
def read_pronunciations_by_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """获取单词的所有发音"""
    return get_pronunciations_by_word(db, word_id)

@router.get("/{pronunciation_id}", response_model=WordPronunciationRead)
def read_pronunciation_endpoint(pronunciation_id: int, db: Session = Depends(get_db)):
    """根据ID获取发音"""
    pronunciation = get_pronunciation(db, pronunciation_id)
    if not pronunciation:
        raise HTTPException(status_code=404, detail="发音未找到")
    return pronunciation

@router.put("/{pronunciation_id}", response_model=WordPronunciationRead)
def update_pronunciation_endpoint(pronunciation_id: int, pronunciation_update: WordPronunciationUpdate, db: Session = Depends(get_db)):
    """更新发音"""
    pronunciation = update_pronunciation(db, pronunciation_id, pronunciation_update)
    if not pronunciation:
        raise HTTPException(status_code=404, detail="发音未找到")
    return pronunciation

@router.delete("/{pronunciation_id}")
def delete_pronunciation_endpoint(pronunciation_id: int, db: Session = Depends(get_db)):
    """删除发音"""
    success = delete_pronunciation(db, pronunciation_id)
    if not success:
        raise HTTPException(status_code=404, detail="发音未找到")
    return {"message": "发音已删除"}