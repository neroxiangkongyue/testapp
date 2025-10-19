# crud/definition.py
from sqlmodel import select, Session
from typing import List, Optional

from app.models.word import WordDefinition
from app.schemas.word_relation import WordDefinitionCreate, WordDefinitionUpdate


def create_definition(db: Session, definition: WordDefinitionCreate) -> WordDefinition:
    """创建新释义"""
    db_definition = WordDefinition.model_validate(definition)
    db.add(db_definition)
    db.commit()
    db.refresh(db_definition)
    return db_definition


def get_definition(db: Session, definition_id: int) -> Optional[WordDefinition]:
    """根据ID获取释义"""
    return db.get(WordDefinition, definition_id)


def get_definitions_by_word(db: Session, word_id: int) -> List[WordDefinition]:
    """获取单词的所有释义"""
    statement = select(WordDefinition).where(WordDefinition.word_id == word_id)
    return db.execute(statement).scalars().all()


def update_definition(db: Session, definition_id: int, definition_update: WordDefinitionUpdate) -> Optional[
    WordDefinition]:
    """更新释义"""
    db_definition = db.get(WordDefinition, definition_id)
    if not db_definition:
        return None

    update_data = definition_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_definition, field, value)

    db.add(db_definition)
    db.commit()
    db.refresh(db_definition)
    return db_definition


def delete_definition(db: Session, definition_id: int) -> bool:
    """删除释义"""
    db_definition = db.get(WordDefinition, definition_id)
    if not db_definition:
        return False

    db.delete(db_definition)
    db.commit()
    return True
