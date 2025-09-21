# api/endpoints/definition.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.crud.word import get_word
from app.database import get_db
from app.schemas.word import WordDefinitionCreate, WordDefinitionRead, WordDefinitionUpdate
from app.crud.definition import (
    create_definition, get_definition, get_definitions_by_word,
    update_definition, delete_definition
)

router = APIRouter(prefix="/definitions", tags=["definitions"])


@router.post("/", response_model=WordDefinitionRead)
def create_definition_endpoint(definition: WordDefinitionCreate, db: Session = Depends(get_db)):
    """创建新释义"""
    word = get_word(db, definition.word_id)
    if not word:
        raise HTTPException(status_code=404, detail="单词未找到")
    return create_definition(db, definition)


@router.get("/word/{word_id}", response_model=List[WordDefinitionRead])
def read_definitions_by_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """获取单词的所有释义"""
    return get_definitions_by_word(db, word_id)


@router.get("/{definition_id}", response_model=WordDefinitionRead)
def read_definition_endpoint(definition_id: int, db: Session = Depends(get_db)):
    """根据ID获取释义"""
    definition = get_definition(db, definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="释义未找到")
    return definition


@router.put("/{definition_id}", response_model=WordDefinitionRead)
def update_definition_endpoint(definition_id: int, definition_update: WordDefinitionUpdate,
                               db: Session = Depends(get_db)):
    """更新释义"""
    definition = update_definition(db, definition_id, definition_update)
    if not definition:
        raise HTTPException(status_code=404, detail="释义未找到")
    return definition


@router.delete("/{definition_id}")
def delete_definition_endpoint(definition_id: int, db: Session = Depends(get_db)):
    """删除释义"""
    success = delete_definition(db, definition_id)
    if not success:
        raise HTTPException(status_code=404, detail="释义未找到")
    return {"message": "释义已删除"}
