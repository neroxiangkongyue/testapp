# api/endpoints/form.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_db
from app.schemas.word import WordFormCreate, WordFormRead, WordFormUpdate
from app.crud.form import (
    create_form, get_form, get_forms_by_word,
    update_form, delete_form
)

router = APIRouter(prefix="/forms", tags=["forms"])

@router.post("/", response_model=WordFormRead)
def create_form_endpoint(form: WordFormCreate, db: Session = Depends(get_db)):
    """创建新词形变化"""
    return create_form(db, form)

@router.get("/word/{word_id}", response_model=List[WordFormRead])
def read_forms_by_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """获取单词的所有词形变化"""
    return get_forms_by_word(db, word_id)

@router.get("/{form_id}", response_model=WordFormRead)
def read_form_endpoint(form_id: int, db: Session = Depends(get_db)):
    """根据ID获取词形变化"""
    form = get_form(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="词形变化未找到")
    return form

@router.put("/{form_id}", response_model=WordFormRead)
def update_form_endpoint(form_id: int, form_update: WordFormUpdate, db: Session = Depends(get_db)):
    """更新词形变化"""
    form = update_form(db, form_id, form_update)
    if not form:
        raise HTTPException(status_code=404, detail="词形变化未找到")
    return form

@router.delete("/{form_id}")
def delete_form_endpoint(form_id: int, db: Session = Depends(get_db)):
    """删除词形变化"""
    success = delete_form(db, form_id)
    if not success:
        raise HTTPException(status_code=404, detail="词形变化未找到")
    return {"message": "词形变化已删除"}