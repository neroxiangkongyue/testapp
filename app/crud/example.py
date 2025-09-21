# crud/example.py
from sqlmodel import select, Session
from typing import List, Optional
from app.models.word import Example
from app.schemas.word import ExampleCreate, ExampleUpdate


def create_example(db: Session, example: ExampleCreate) -> Example:
    """创建新例句"""
    db_example = Example.model_validate(example)
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example


def get_example(db: Session, example_id: int) -> Optional[Example]:
    """根据ID获取例句"""
    return db.get(Example, example_id)


def get_examples_by_word(db: Session, word_id: int) -> List[Example]:
    """获取单词的所有例句"""
    statement = select(Example).where(Example.word_id == word_id)
    return db.execute(statement).scalars().all()


def update_example(db: Session, example_id: int, example_update: ExampleUpdate) -> Optional[Example]:
    """更新例句"""
    db_example = db.get(Example, example_id)
    if not db_example:
        return None

    update_data = example_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_example, field, value)

    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example


def delete_example(db: Session, example_id: int) -> bool:
    """删除例句"""
    db_example = db.get(Example, example_id)
    if not db_example:
        return False

    db.delete(db_example)
    db.commit()
    return True