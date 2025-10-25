# crud/pronunciation.py
from sqlmodel import select, Session
from typing import List, Optional
from app.models.word import WordPronunciation
from app.schemas.word_relation import WordPronunciationCreate, WordPronunciationUpdate


def create_pronunciation(db: Session, pronunciation: WordPronunciationCreate) -> WordPronunciation:
    """创建新发音"""
    db_pronunciation = WordPronunciation.model_validate(pronunciation)
    db.add(db_pronunciation)
    db.commit()
    db.refresh(db_pronunciation)
    return db_pronunciation


def get_pronunciation(db: Session, pronunciation_id: int) -> Optional[WordPronunciation]:
    """根据ID获取发音"""
    return db.get(WordPronunciation, pronunciation_id)


def get_pronunciations_by_word(db: Session, word_id: int) -> List[WordPronunciation]:
    """获取单词的所有发音"""
    statement = select(WordPronunciation).where(WordPronunciation.word_id == word_id)
    return db.execute(statement).scalars().all()


def update_pronunciation(db: Session, pronunciation_id: int, pronunciation_update: WordPronunciationUpdate) -> Optional[
    WordPronunciation]:
    """更新发音"""
    db_pronunciation = db.get(WordPronunciation, pronunciation_id)
    if not db_pronunciation:
        return None

    update_data = pronunciation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pronunciation, field, value)

    db.add(db_pronunciation)
    db.commit()
    db.refresh(db_pronunciation)
    return db_pronunciation


def delete_pronunciation(db: Session, pronunciation_id: int) -> bool:
    """删除发音"""
    db_pronunciation = db.get(WordPronunciation, pronunciation_id)
    if not db_pronunciation:
        return False

    db.delete(db_pronunciation)
    db.commit()
    return True