# api/endpoints/example.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_db
from app.schemas.word import ExampleCreate, ExampleRead, ExampleUpdate
from app.crud.example import (
    create_example, get_example, get_examples_by_word,
    update_example, delete_example
)

router = APIRouter(prefix="/examples", tags=["examples"])

@router.post("/", response_model=ExampleRead)
def create_example_endpoint(example: ExampleCreate, db: Session = Depends(get_db)):
    """创建新例句"""
    return create_example(db, example)

@router.get("/word/{word_id}", response_model=List[ExampleRead])
def read_examples_by_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """获取单词的所有例句"""
    return get_examples_by_word(db, word_id)

@router.get("/{example_id}", response_model=ExampleRead)
def read_example_endpoint(example_id: int, db: Session = Depends(get_db)):
    """根据ID获取例句"""
    example = get_example(db, example_id)
    if not example:
        raise HTTPException(status_code=404, detail="例句未找到")
    return example

@router.put("/{example_id}", response_model=ExampleRead)
def update_example_endpoint(example_id: int, example_update: ExampleUpdate, db: Session = Depends(get_db)):
    """更新例句"""
    example = update_example(db, example_id, example_update)
    if not example:
        raise HTTPException(status_code=404, detail="例句未找到")
    return example

@router.delete("/{example_id}")
def delete_example_endpoint(example_id: int, db: Session = Depends(get_db)):
    """删除例句"""
    success = delete_example(db, example_id)
    if not success:
        raise HTTPException(status_code=404, detail="例句未找到")
    return {"message": "例句已删除"}