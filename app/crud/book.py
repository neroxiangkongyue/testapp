from sqlmodel import and_, or_, desc, select
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.book import (
    Wordbook, RelationBook, WordbookWordLink, RelationBookRelationLink,
    UserWordbookCollectionLink, UserRelationBookCollectionLink
)
from app.schemas.book import WordbookCreate, WordbookUpdate, RelationBookCreate, RelationBookUpdate
from app.crud.word import get_word
from app.crud.relation import get_relation


# ===== 词库相关操作 =====
def create_wordbook(db: Session, wordbook_data: WordbookCreate, creator_id: int) -> Wordbook:
    """创建词库"""
    wordbook = Wordbook(
        name=wordbook_data.name,
        description=wordbook_data.description,
        is_public=wordbook_data.is_public,
        cover_image=wordbook_data.cover_image,
        creator_id=creator_id
    )
    db.add(wordbook)
    db.commit()
    db.refresh(wordbook)
    return wordbook


def get_wordbook(db: Session, wordbook_id: int) -> Optional[Wordbook]:
    """获取单个词库"""
    return db.get(Wordbook, wordbook_id)


def get_wordbook_with_visibility_check(
        db: Session,
        wordbook_id: int,
        user_id: Optional[int] = None
) -> Optional[Wordbook]:
    """获取词库并检查可见性"""
    wordbook = get_wordbook(db, wordbook_id)

    if not wordbook:
        return None

    # 检查可见性：公开词库或用户自己的私有词库
    if wordbook.is_public:
        return wordbook
    elif not wordbook.is_public and user_id and wordbook.creator_id == user_id:
        return wordbook

    return None


def get_wordbooks(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        is_public: Optional[bool] = None,
        keyword: Optional[str] = None
) -> List[Wordbook]:
    """获取词库列表（考虑可见性）"""
    statement = select(Wordbook)

    # 过滤条件
    if user_id:
        statement = statement.where(Wordbook.creator_id == user_id)
    else:
        # 如果没有指定用户，只显示公开词库
        statement = statement.where(Wordbook.is_public == True)

    if is_public is not None:
        statement = statement.where(Wordbook.is_public == is_public)

    if keyword:
        statement = statement.where(or_(
            Wordbook.name.ilike(f"%{keyword}%"),
            Wordbook.description.ilike(f"%{keyword}%")
        ))

    statement = statement.offset(skip).limit(limit).order_by(desc(Wordbook.created_at))
    return db.execute(statement).scalars().all()


def get_user_wordbooks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Wordbook]:
    """获取用户创建的词库（包括私有词库）"""
    statement = select(Wordbook).where(
        Wordbook.creator_id == user_id
    ).offset(skip).limit(limit).order_by(desc(Wordbook.created_at))
    return db.execute(statement).scalars().all()


def get_collected_wordbooks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Wordbook]:
    """获取用户收藏的词库（只包括公开词库和用户自己的私有词库）"""
    # 获取用户收藏的所有词库ID
    collection_statement = select(UserWordbookCollectionLink.wordbook_id).where(
        UserWordbookCollectionLink.user_id == user_id
    )
    collected_wordbook_ids = db.execute(collection_statement).scalars().all()

    if not collected_wordbook_ids:
        return []

    # 获取词库，只包括公开词库和用户自己的词库
    statement = select(Wordbook).where(
        Wordbook.id.in_(collected_wordbook_ids),
        or_(
            Wordbook.is_public == True,
            Wordbook.creator_id == user_id
        )
    ).order_by(desc(Wordbook.created_at)).offset(skip).limit(limit)
    return db.execute(statement).scalars().all()


def update_wordbook(db: Session, wordbook: Wordbook, wordbook_data: WordbookUpdate) -> Wordbook:
    """更新词库"""
    wordbook_data_dict = wordbook_data.dict(exclude_unset=True)

    for field, value in wordbook_data_dict.items():
        setattr(wordbook, field, value)

    db.add(wordbook)
    db.commit()
    db.refresh(wordbook)
    return wordbook


def delete_wordbook(db: Session, wordbook: Wordbook) -> bool:
    """删除词库及其关联"""
    try:
        # 删除单词关联
        delete_statement = WordbookWordLink.__table__.delete().where(WordbookWordLink.wordbook_id == wordbook.id)
        db.execute(delete_statement)
        # 删除收藏关联
        delete_statement = UserWordbookCollectionLink.__table__.delete().where(
            UserWordbookCollectionLink.wordbook_id == wordbook.id)
        db.execute(delete_statement)
        # 删除词库
        db.delete(wordbook)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def add_word_to_wordbook(db: Session, wordbook_id: int, word_id: int, order: int = 0,
                         note: Optional[str] = None) -> bool:
    """添加单词到词库"""
    # 检查单词是否存在
    word = get_word(db, word_id)
    if not word:
        return False

    # 检查是否已存在关联
    existing_statement = select(WordbookWordLink).where(
        and_(
            WordbookWordLink.wordbook_id == wordbook_id,
            WordbookWordLink.word_id == word_id
        )
    )
    existing = db.execute(existing_statement).scalars().first()

    if existing:
        return False  # 已经存在关联

    # 添加关联
    wordbook_word_link = WordbookWordLink(
        wordbook_id=wordbook_id,
        word_id=word_id,
        order=order,
        note=note
    )
    db.add(wordbook_word_link)

    # 更新单词计数
    wordbook = get_wordbook(db, wordbook_id)
    if wordbook:
        wordbook.word_count += 1
        db.add(wordbook)

    db.commit()
    return True


def remove_word_from_wordbook(db: Session, wordbook_id: int, word_id: int) -> bool:
    """从词库移除单词"""
    # 查找关联记录
    link_statement = select(WordbookWordLink).where(
        and_(
            WordbookWordLink.wordbook_id == wordbook_id,
            WordbookWordLink.word_id == word_id
        )
    )
    link = db.execute(link_statement).scalars().first()

    if not link:
        return False

    # 删除关联
    db.delete(link)

    # 更新单词计数
    wordbook = get_wordbook(db, wordbook_id)
    if wordbook and wordbook.word_count > 0:
        wordbook.word_count -= 1
        db.add(wordbook)

    db.commit()
    return True


def get_wordbook_words(db: Session, wordbook_id: int) -> List[int]:
    """获取词库关联的单词ID列表"""
    statement = select(WordbookWordLink.word_id).where(WordbookWordLink.wordbook_id == wordbook_id)
    return db.execute(statement).scalars().all()


def collect_wordbook(db: Session, wordbook_id: int, user_id: int) -> bool:
    """收藏词库（只允许收藏公开词库）"""
    wordbook = get_wordbook(db, wordbook_id)

    # 只能收藏公开词库
    if not wordbook or not wordbook.is_public:
        return False

    # 检查是否已收藏
    existing_statement = select(UserWordbookCollectionLink).where(
        and_(
            UserWordbookCollectionLink.user_id == user_id,
            UserWordbookCollectionLink.wordbook_id == wordbook_id
        )
    )
    existing = db.execute(existing_statement).scalars().first()

    if existing:
        return False  # 已经收藏过了

    # 添加收藏
    collection = UserWordbookCollectionLink(
        user_id=user_id,
        wordbook_id=wordbook_id
    )
    db.add(collection)
    db.commit()
    return True


def uncollect_wordbook(db: Session, wordbook_id: int, user_id: int) -> bool:
    """取消收藏词库"""
    # 查找收藏记录
    collection_statement = select(UserWordbookCollectionLink).where(
        and_(
            UserWordbookCollectionLink.user_id == user_id,
            UserWordbookCollectionLink.wordbook_id == wordbook_id
        )
    )
    collection = db.execute(collection_statement).scalars().first()

    if not collection:
        return False  # 没有收藏记录

    # 删除收藏
    db.delete(collection)
    db.commit()
    return True


def check_wordbook_collected(db: Session, wordbook_id: int, user_id: int) -> bool:
    """检查用户是否收藏了词库"""
    collection_statement = select(UserWordbookCollectionLink).where(
        and_(
            UserWordbookCollectionLink.user_id == user_id,
            UserWordbookCollectionLink.wordbook_id == wordbook_id
        )
    )
    collection = db.execute(collection_statement).scalars().first()
    return collection is not None


# ===== 关系库相关操作 =====
def create_relation_book(db: Session, relation_book_data: RelationBookCreate, creator_id: int) -> RelationBook:
    """创建关系库"""
    relation_book = RelationBook(
        name=relation_book_data.name,
        description=relation_book_data.description,
        is_public=relation_book_data.is_public,
        cover_image=relation_book_data.cover_image,
        creator_id=creator_id
    )
    db.add(relation_book)
    db.commit()
    db.refresh(relation_book)
    return relation_book


def get_relation_book(db: Session, relation_book_id: int) -> Optional[RelationBook]:
    """获取单个关系库"""
    return db.get(RelationBook, relation_book_id)


def get_relation_book_with_visibility_check(
        db: Session,
        relation_book_id: int,
        user_id: Optional[int] = None
) -> Optional[RelationBook]:
    """获取关系库并检查可见性"""
    relation_book = get_relation_book(db, relation_book_id)

    if not relation_book:
        return None

    # 检查可见性：公开关系库或用户自己的私有关系库
    if relation_book.is_public:
        return relation_book
    elif not relation_book.is_public and user_id and relation_book.creator_id == user_id:
        return relation_book

    return None


def get_relation_books(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        is_public: Optional[bool] = None,
        keyword: Optional[str] = None
) -> List[RelationBook]:
    """获取关系库列表（考虑可见性）"""
    statement = select(RelationBook)

    # 过滤条件
    if user_id:
        statement = statement.where(RelationBook.creator_id == user_id)
    else:
        # 如果没有指定用户，只显示公开关系库
        statement = statement.where(RelationBook.is_public == True)

    if is_public is not None:
        statement = statement.where(RelationBook.is_public == is_public)

    if keyword:
        statement = statement.where(or_(
            RelationBook.name.ilike(f"%{keyword}%"),
            RelationBook.description.ilike(f"%{keyword}%")
        ))

    statement = statement.offset(skip).limit(limit).order_by(desc(RelationBook.created_at))
    return db.execute(statement).scalars().all()


def get_user_relation_books(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[RelationBook]:
    """获取用户创建的关系库（包括私有关系库）"""
    statement = select(RelationBook).where(
        RelationBook.creator_id == user_id
    ).offset(skip).limit(limit).order_by(desc(RelationBook.created_at))
    return db.execute(statement).scalars().all()


def get_collected_relation_books(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[RelationBook]:
    """获取用户收藏的关系库（只包括公开关系库和用户自己的私有关系库）"""
    # 获取用户收藏的所有关系库ID
    collection_statement = select(UserRelationBookCollectionLink.relation_book_id).where(
        UserRelationBookCollectionLink.user_id == user_id
    )
    collected_relation_book_ids = db.execute(collection_statement).scalars().all()

    if not collected_relation_book_ids:
        return []

    # 获取关系库，只包括公开关系库和用户自己的关系库
    statement = select(RelationBook).where(
        RelationBook.id.in_(collected_relation_book_ids),
        or_(
            RelationBook.is_public == True,
            RelationBook.creator_id == user_id
        )
    ).order_by(desc(RelationBook.created_at)).offset(skip).limit(limit)
    return db.execute(statement).scalars().all()


def update_relation_book(db: Session, relation_book: RelationBook,
                         relation_book_data: RelationBookUpdate) -> RelationBook:
    """更新关系库"""
    relation_book_data_dict = relation_book_data.dict(exclude_unset=True)

    for field, value in relation_book_data_dict.items():
        setattr(relation_book, field, value)

    db.add(relation_book)
    db.commit()
    db.refresh(relation_book)
    return relation_book


def delete_relation_book(db: Session, relation_book: RelationBook) -> bool:
    """删除关系库及其关联"""
    try:
        # 删除关系关联
        delete_statement = RelationBookRelationLink.__table__.delete().where(
            RelationBookRelationLink.relation_book_id == relation_book.id)
        db.execute(delete_statement)
        # 删除收藏关联
        delete_statement = UserRelationBookCollectionLink.__table__.delete().where(
            UserRelationBookCollectionLink.relation_book_id == relation_book.id)
        db.execute(delete_statement)
        # 删除关系库
        db.delete(relation_book)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def add_relation_to_relation_book(db: Session, relation_book_id: int, relation_id: int, order: int = 0,
                                  note: Optional[str] = None) -> bool:
    """添加关系到关系库"""
    # 检查关系是否存在
    relation = get_relation(db, relation_id)
    if not relation:
        return False

    # 检查是否已存在关联
    existing_statement = select(RelationBookRelationLink).where(
        and_(
            RelationBookRelationLink.relation_book_id == relation_book_id,
            RelationBookRelationLink.relation_id == relation_id
        )
    )
    existing = db.execute(existing_statement).scalars().first()

    if existing:
        return False  # 已经存在关联

    # 添加关联
    relation_book_relation_link = RelationBookRelationLink(
        relation_book_id=relation_book_id,
        relation_id=relation_id,
        order=order,
        note=note
    )
    db.add(relation_book_relation_link)

    # 更新关系计数
    relation_book = get_relation_book(db, relation_book_id)
    if relation_book:
        relation_book.relation_count += 1
        db.add(relation_book)

    db.commit()
    return True


def remove_relation_from_relation_book(db: Session, relation_book_id: int, relation_id: int) -> bool:
    """从关系库移除关系"""
    # 查找关联记录
    link_statement = select(RelationBookRelationLink).where(
        and_(
            RelationBookRelationLink.relation_book_id == relation_book_id,
            RelationBookRelationLink.relation_id == relation_id
        )
    )
    link = db.execute(link_statement).scalars().first()

    if not link:
        return False

    # 删除关联
    db.delete(link)

    # 更新关系计数
    relation_book = get_relation_book(db, relation_book_id)
    if relation_book and relation_book.relation_count > 0:
        relation_book.relation_count -= 1
        db.add(relation_book)

    db.commit()
    return True


def get_relation_book_relations(db: Session, relation_book_id: int) -> List[int]:
    """获取关系库关联的关系ID列表"""
    statement = select(RelationBookRelationLink.relation_id).where(
        RelationBookRelationLink.relation_book_id == relation_book_id)
    return db.execute(statement).scalars().all()


def collect_relation_book(db: Session, relation_book_id: int, user_id: int) -> bool:
    """收藏关系库（只允许收藏公开关系库）"""
    relation_book = get_relation_book(db, relation_book_id)

    # 只能收藏公开关系库
    if not relation_book or not relation_book.is_public:
        return False

    # 检查是否已收藏
    existing_statement = select(UserRelationBookCollectionLink).where(
        and_(
            UserRelationBookCollectionLink.user_id == user_id,
            UserRelationBookCollectionLink.relation_book_id == relation_book_id
        )
    )
    existing = db.execute(existing_statement).scalars().first()

    if existing:
        return False  # 已经收藏过了

    # 添加收藏
    collection = UserRelationBookCollectionLink(
        user_id=user_id,
        relation_book_id=relation_book_id
    )
    db.add(collection)
    db.commit()
    return True


def uncollect_relation_book(db: Session, relation_book_id: int, user_id: int) -> bool:
    """取消收藏关系库"""
    # 查找收藏记录
    collection_statement = select(UserRelationBookCollectionLink).where(
        and_(
            UserRelationBookCollectionLink.user_id == user_id,
            UserRelationBookCollectionLink.relation_book_id == relation_book_id
        )
    )
    collection = db.execute(collection_statement).scalars().first()

    if not collection:
        return False  # 没有收藏记录

    # 删除收藏
    db.delete(collection)
    db.commit()
    return True


def check_relation_book_collected(db: Session, relation_book_id: int, user_id: int) -> bool:
    """检查用户是否收藏了关系库"""
    collection_statement = select(UserRelationBookCollectionLink).where(
        and_(
            UserRelationBookCollectionLink.user_id == user_id,
            UserRelationBookCollectionLink.relation_book_id == relation_book_id
        )
    )
    collection = db.execute(collection_statement).scalars().first()
    return collection is not None
