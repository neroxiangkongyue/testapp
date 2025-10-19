# app/routers/word_definition.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from typing import List

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Word
from app.models.user import User
from app.models.word import WordDefinition
from app.schemas.word_relation import WordDefinitionCreate, WordDefinitionRead, WordDefinitionUpdate
from app.crud.word_relation import (
    get_word_definitions, get_definition_by_id, create_word_definition,
    update_word_definition, get_word_id_by_text, is_exist_definition, delete_word_definition
)

word_definition_router = APIRouter(prefix="/words/{word_text}/definitions", tags=["word definitions"])


@word_definition_router.get("/", response_model=List[WordDefinitionRead])
def read_word_definitions(word_text: str, db: Session = Depends(get_db)):
    """获取单词的所有定义"""
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    definitions = get_word_definitions(db, word_id)
    return definitions


@word_definition_router.get("/{definition_id}", response_model=WordDefinitionRead)
def read_word_definition_by_id(definition_id: int, db: Session = Depends(get_db)):
    """通过定义id获取单词的定义"""
    definition = get_definition_by_id(db, definition_id)
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Definition not found"
        )
    return definition


@word_definition_router.post("/", response_model=WordDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_definition(
        word_text: str,
        definition: WordDefinitionCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """为单词创建新定义"""
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

    db_definition = create_word_definition(db, word_id, definition.dict())
    return db_definition


@word_definition_router.put("/{definition_id}", response_model=WordDefinitionRead)
def update_definition(
        word_text: str,
        definition_id: int,
        definition_update: WordDefinitionUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新单词的定义"""
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
    # 验证定义存在且属于该单词
    exist_definition = is_exist_definition(db, definition_id, word_id)
    if not exist_definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Definition not found"
        )
    # 更新定义
    update_data = definition_update.dict(exclude_unset=True)
    db_definition = update_word_definition(db, definition_id, update_data)
    return db_definition


@word_definition_router.delete("/{definition_id}")
def delete_definition(
        word_text: str,
        definition_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """安全删除单词的指定定义"""
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

    # 验证定义存在且属于该单词
    exist_definition = is_exist_definition(db, definition_id, word_id)
    if not exist_definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Definition not found"
        )

    # 执行删除
    is_delete_definition = delete_word_definition(db, definition_id)
    if is_delete_definition:
        return {"message": "定义删除成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败"
        )

