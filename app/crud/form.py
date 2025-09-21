# crud/form.py
from sqlmodel import select, Session
from typing import List, Optional
from app.models.word import WordForm
from app.schemas.word import WordFormCreate, WordFormUpdate


def create_form(db: Session, form: WordFormCreate) -> WordForm:
    """创建新词形变化"""
    db_form = WordForm.model_validate(form)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form


def get_form(db: Session, form_id: int) -> Optional[WordForm]:
    """根据ID获取词形变化"""
    return db.get(WordForm, form_id)


def get_forms_by_word(db: Session, word_id: int) -> List[WordForm]:
    """获取单词的所有词形变化"""
    statement = select(WordForm).where(WordForm.word_id == word_id)
    return db.execute(statement).scalars().all()


def update_form(db: Session, form_id: int, form_update: WordFormUpdate) -> Optional[WordForm]:
    """更新词形变化"""
    db_form = db.get(WordForm, form_id)
    if not db_form:
        return None

    update_data = form_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_form, field, value)

    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form


def delete_form(db: Session, form_id: int) -> bool:
    """删除词形变化"""
    db_form = db.get(WordForm, form_id)
    if not db_form:
        return False

    db.delete(db_form)
    db.commit()
    return True