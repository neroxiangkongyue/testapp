# crud/word.py
import json

from sqlmodel import select, Session
from typing import List, Optional

from app.models.word import Word
from app.schemas.word import WordCreate, WordUpdate


def create_word(db: Session, word: WordCreate) -> Word:
    """创建新单词"""
    # 将WordCreate转换为字典
    word_data = word.model_dump()

    # 处理tags字段
    if 'tags' in word_data:
        tags = word_data.pop('tags')
        word_data['tags_json'] = json.dumps(tags) if tags else None
    db_word = Word(**word_data)  # 推荐：直接从字典创建 SQLModel 实例
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


def get_word(db: Session, word_id: int) -> Optional[Word]:
    """根据ID获取单词"""
    return db.get(Word, word_id)


def get_by_word(db: Session, word_text: str) -> Optional[Word]:
    statement = select(Word).where(
        (Word.word == word_text) |
        (Word.normalized_word == word_text.lower())
    )
    word = db.scalars(statement).first()
    return word


def get_word_by_normalized(db: Session, normalized_word: str) -> Optional[Word]:
    """根据标准化单词获取单词"""
    statement = select(Word).where(Word.normalized_word == normalized_word)
    return db.execute(statement).scalars().first()


def get_words(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_common: Optional[bool] = None,
        difficulty_level_id: Optional[int] = None
) -> List[Word]:
    # 创建查询语句
    query = db.query(Word)

    # 添加过滤条件
    if is_common is not None:
        query = query.filter(Word.is_common == is_common)

    if difficulty_level_id is not None:
        query = query.filter(Word.difficulty_level_id == difficulty_level_id)

    # 添加分页
    query = query.offset(skip).limit(limit)

    # 执行查询并返回结果
    return query.all()


def update_word(db: Session, word_id: int, word_update: WordUpdate) -> Optional[Word]:
    """更新单词"""
    db_word = db.get(Word, word_id)
    if not db_word:
        return None

    # 只更新提供的字段
    update_data = word_update.model_dump(exclude_unset=True)
    # 检查 normalized_word 是否已存在（除了当前单词）
    if 'normalized_word' in update_data:
        new_normalized = update_data['normalized_word']
        # 检查是否有其他单词使用相同的 normalized_word
        existing_word = db.execute(
            select(Word).where(
                Word.normalized_word == new_normalized,
                Word.id != word_id
            )
        ).scalars().first()

        if existing_word:
            return None
    # 处理tags字段
    if 'tags' in update_data:
        tags = update_data.pop('tags')
        update_data['tags_json'] = json.dumps(tags) if tags else None
    for field, value in update_data.items():
        setattr(db_word, field, value)

    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


def delete_word(db: Session, word_id: int) -> bool:
    """删除单词"""
    db_word = db.get(Word, word_id)
    if not db_word:
        return False

    db.delete(db_word)
    db.commit()
    return True


def search_words(db: Session, query: str, limit: int = 20) -> List[Word]:
    """搜索单词"""
    statement = select(Word).where(
        (Word.word.ilike(f"%{query}%")) |
        (Word.normalized_word.ilike(f"%{query}%"))
    ).limit(limit)
    return db.execute(statement).scalars().all()