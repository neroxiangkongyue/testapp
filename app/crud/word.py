# app/crud/word.py
from sqlmodel import Session, select, or_
from typing import List, Optional

from app.models.word import Word, WordDefinition, Example, WordForm, WordPronunciation, Tag, WordTagLink
from app.schemas.word import WordCreate, WordUpdate

from sqlalchemy.exc import IntegrityError


def get_word_id_by_text(db: Session, word_text: str) -> Optional[int]:
    """通过单词文本获取单词ID"""
    normalized = word_text.lower()
    statement = select(Word).where(
        (Word.word == word_text) |
        (Word.normalized_word == normalized)
    )
    word = db.execute(statement).scalars().first()
    return word.id if word else None


def create_word(db: Session, word_data: WordCreate) -> Optional[Word]:
    """
    创建新单词及其所有关联数据（定义、例句、形式、发音和标签）

    参数:
        db: 数据库会话
        word_data: 包含单词及其关联数据的创建对象

    返回:
        成功时返回创建的Word对象，如果单词已存在则返回None
    """
    try:
        # 1. 检查单词是否已存在（不区分大小写）
        normalized_word = word_data.word.lower()
        existing_word = db.execute(
            select(Word).where(Word.normalized_word == normalized_word)
        ).first()

        if existing_word:
            return None  # 单词已存在

        # 2. 创建单词主体
        db_word = Word(
            word=word_data.word,
            normalized_word=normalized_word,
            length=len(word_data.word),
            frequency_rank=word_data.frequency_rank,
            difficulty_level=word_data.difficulty_level,
            is_common=word_data.is_common,
            etymology=word_data.etymology,
            description=word_data.description
        )
        db.add(db_word)
        db.commit()  # 先提交以获取word_id

        # 3. 处理单词定义
        for definition in word_data.definitions:
            db_definition = WordDefinition(
                word_id=db_word.id,
                **definition.dict(exclude_unset=True)
            )
            db.add(db_definition)

        # 4. 处理例句
        for example in word_data.examples:
            db_example = Example(
                word_id=db_word.id,
                **example.dict(exclude_unset=True)
            )
            db.add(db_example)

        # 5. 处理单词形式
        for form in word_data.forms:
            db_form = WordForm(
                word_id=db_word.id,
                **form.dict(exclude_unset=True)
            )
            db.add(db_form)

        # 6. 处理发音
        for pronunciation in word_data.pronunciations:
            db_pronunciation = WordPronunciation(
                word_id=db_word.id,
                **pronunciation.dict(exclude_unset=True)
            )
            db.add(db_pronunciation)

        # 7. 处理标签（先查找或创建标签，然后建立关联）
        for tag_data in word_data.tags:
            # 查找标签 - 使用 scalars() 获取 Tag 对象
            stmt = select(Tag).where(Tag.name == tag_data.name)
            db_tag = db.scalars(stmt).first()

            if not db_tag:
                # 创建新标签
                db_tag = Tag(**tag_data.dict(exclude_unset=True))
                db.add(db_tag)
                db.commit()  # 提交以获取tag_id
                db.refresh(db_tag)  # 刷新以获取id属性

            # 创建关联关系
            db.add(WordTagLink(word_id=db_word.id, tag_id=db_tag.id))

        db.commit()
        db.refresh(db_word)
        return db_word

    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"创建单词时发生完整性错误: {str(e)}")
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"创建单词时发生错误: {str(e)}")

def get_word(db: Session, word_id: int) -> Optional[Word]:
    """根据ID获取单词"""
    return db.get(Word, word_id)


def get_word_by_word(db: Session, word_text: str) -> Optional[Word]:
    """通过单词文本获取单词"""
    normalized = word_text.lower()
    statement = select(Word).where(
        (Word.word == word_text) |
        (Word.normalized_word == normalized)
    )
    return db.execute(statement).scalars().first()


def get_words(db: Session, skip: int = 0, limit: int = 100) -> List[Word]:
    """获取单词列表（分页）"""
    statement = select(Word).offset(skip).limit(limit)
    return db.execute(statement).scalars().all()


def update_word(db: Session, word_id: int, word_update: WordUpdate) -> Optional[Word]:
    """更新单词"""
    db_word = db.get(Word, word_id)
    if not db_word:
        return None

    update_data = word_update.dict(exclude_unset=True)
    if 'word' in update_data:
        update_data['normalized_word'] = update_data['word'].lower()
        update_data['length'] = len(update_data['word'])
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
    normalized_query = query.lower()
    statement = select(Word).where(
        or_(
            Word.word.ilike(f"%{normalized_query}%"),
            Word.normalized_word.ilike(f"%{normalized_query}%")
        )
    ).limit(limit)
    return db.execute(statement).scalars().all()


def increment_view_count(db: Session, word_id: int) -> Optional[Word]:
    """增加浏览计数"""
    db_word = db.get(Word, word_id)
    if not db_word:
        return None
    db_word.view_count += 1
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


def update_user_feedback(db: Session, word_id: int, feedback_type: str) -> Optional[Word]:
    """更新用户反馈统计（认识、不认识、不确定）"""
    db_word = db.get(Word, word_id)
    if not db_word:
        return None

    if feedback_type == "known":
        db_word.known_count += 1
    elif feedback_type == "unknown":
        db_word.unknown_count += 1
    elif feedback_type == "uncertain":
        db_word.uncertain_count += 1
    else:
        return None

    # 重新计算难度等级
    db_word.difficulty_level = db_word.calculated_difficulty_level

    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word