# app/routers/word_forms.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.word_relation import WordFormCreate, WordFormRead, WordFormUpdate
from app.crud.word_relation import (
    get_word_forms, get_form_by_id, create_word_form,
    update_word_form, delete_word_form, is_exist_form, get_word_id_by_text
)

word_form_router = APIRouter(prefix="/words/{word_text}/forms", tags=["word forms"])


@word_form_router.get("/", response_model=List[WordFormRead])
def read_word_forms(word_text: str, db: Session = Depends(get_db)):
    """获取单词的所有形式"""
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    forms = get_word_forms(db, word_id)
    return forms


@word_form_router.get("/{form_id}", response_model=WordFormRead)
def read_word_form_by_id(form_id: int, db: Session = Depends(get_db)):
    """通过形式id获取单词的形式"""
    form = get_form_by_id(db, form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    return form


@word_form_router.post("/", response_model=WordFormRead, status_code=status.HTTP_201_CREATED)
def create_form(
        word_text: str,
        form: WordFormCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """为单词创建新形式"""
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

    db_form = create_word_form(db, word_id, form.dict())
    return db_form


@word_form_router.put("/{form_id}", response_model=WordFormRead)
def update_form(
        word_text: str,
        form_id: int,
        form_update: WordFormUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新单词的形式"""
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

    # 验证形式存在且属于该单词
    exist_form = is_exist_form(db, form_id, word_id)
    if not exist_form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # 更新形式
    update_data = form_update.dict(exclude_unset=True)
    db_form = update_word_form(db, form_id, update_data)
    return db_form


@word_form_router.delete("/{form_id}")
def delete_form(
        word_text: str,
        form_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """安全删除单词的指定形式"""
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

    # 验证形式存在且属于该单词
    exist_form = is_exist_form(db, form_id, word_id)
    if not exist_form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # 执行删除
    is_delete_form = delete_word_form(db, form_id)
    if is_delete_form:
        return {"message": "Form deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed"
        )