from sqlmodel import and_, or_, desc, select
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.note import Note, NoteWordLink, NoteRelationLink, UserNoteCollectionLink
from app.schemas.note import NoteCreate, NoteUpdate
from app.models.enums import NoteVisibility


def create_note(
        db: Session,
        note_data: NoteCreate,
        creator_id: int,
        word_ids: Optional[List[int]] = None,
        relation_ids: Optional[List[int]] = None
) -> Note:
    """创建笔记"""
    # 创建笔记主体
    note = Note(
        title=note_data.title,
        content=note_data.content,
        visibility=note_data.visibility,
        creator_id=creator_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    # 关联单词
    if word_ids:
        for word_id in word_ids:
            note_word_link = NoteWordLink(note_id=note.id, word_id=word_id)
            db.add(note_word_link)

    # 关联关系
    if relation_ids:
        for relation_id in relation_ids:
            note_relation_link = NoteRelationLink(note_id=note.id, relation_id=relation_id)
            db.add(note_relation_link)

    db.commit()
    db.refresh(note)
    return note


def get_note(db: Session, note_id: int) -> Optional[Note]:
    """获取单个笔记"""
    return db.get(Note, note_id)


def get_note_with_visibility_check(
        db: Session,
        note_id: int,
        user_id: Optional[int] = None
) -> Optional[Note]:
    """获取笔记并检查可见性"""
    note = get_note(db, note_id)

    if not note:
        return None

    # 检查可见性：公开笔记或用户自己的私有笔记
    if note.visibility == NoteVisibility.PUBLIC:
        return note
    elif note.visibility == NoteVisibility.PRIVATE and user_id and note.creator_id == user_id:
        return note

    return None  # 没有权限查看


def get_notes(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        visibility: Optional[NoteVisibility] = None,
        keyword: Optional[str] = None
) -> List[Note]:
    """获取笔记列表（考虑可见性）"""
    statement = select(Note)

    # 过滤条件
    if user_id:
        statement = statement.where(Note.creator_id == user_id)
    else:
        # 如果没有指定用户，只显示公开笔记
        statement = statement.where(Note.visibility == NoteVisibility.PUBLIC)

    if visibility:
        statement = statement.where(Note.visibility == visibility)

    if keyword:
        statement = statement.where(or_(
            Note.title.ilike(f"%{keyword}%"),
            Note.content.ilike(f"%{keyword}%")
        ))

    statement = statement.offset(skip).limit(limit).order_by(desc(Note.created_at))
    return db.execute(statement).scalars().all()


def get_user_notes(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[Note]:
    """获取用户创建的笔记（包括私有笔记）"""
    statement = select(Note).where(
        Note.creator_id == user_id
    ).offset(skip).limit(limit).order_by(desc(Note.created_at))
    return db.execute(statement).scalars().all()


def get_public_notes(
        db: Session,
        skip: int = 0,
        limit: int = 100
) -> List[Note]:
    """获取公开笔记"""
    statement = select(Note).where(
        Note.visibility == NoteVisibility.PUBLIC
    ).offset(skip).limit(limit).order_by(desc(Note.created_at))
    return db.execute(statement).scalars().all()


def get_collected_notes(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[Note]:
    """获取用户收藏的笔记（只包括公开笔记和用户自己的私有笔记）"""
    # 使用 join 查询而不是先获取 ID
    statement = select(Note).join(
        UserNoteCollectionLink,
        Note.id == UserNoteCollectionLink.note_id
    ).where(
        UserNoteCollectionLink.user_id == user_id,
        or_(
            Note.visibility == NoteVisibility.PUBLIC,
            Note.creator_id == user_id
        )
    ).order_by(desc(Note.created_at)).offset(skip).limit(limit)

    return db.execute(statement).scalars().all()


def get_notes_by_word_id(
        db: Session,
        word_id: int,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
) -> List[Note]:
    """通过单词ID查找笔记（考虑可见性）"""
    statement = select(Note).join(
        NoteWordLink,
        Note.id == NoteWordLink.note_id
    ).where(
        NoteWordLink.word_id == word_id
    )

    # 根据可见性过滤
    if user_id:
        statement = statement.where(
            or_(
                Note.visibility == NoteVisibility.PUBLIC,
                Note.creator_id == user_id
            )
        )
    else:
        statement = statement.where(
            Note.visibility == NoteVisibility.PUBLIC
        )

    statement = statement.offset(skip).limit(limit).order_by(desc(Note.created_at))
    return db.execute(statement).scalars().all()


def get_notes_by_relation_id(
        db: Session,
        relation_id: int,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
) -> List[Note]:
    """通过关系ID查找笔记（考虑可见性）"""
    statement = select(Note).join(
        NoteRelationLink,
        Note.id == NoteRelationLink.note_id
    ).where(
        NoteRelationLink.relation_id == relation_id
    )

    # 根据可见性过滤
    if user_id:
        statement = statement.where(
            or_(
                Note.visibility == NoteVisibility.PUBLIC,
                Note.creator_id == user_id
            )
        )
    else:
        statement = statement.where(
            Note.visibility == NoteVisibility.PUBLIC
        )

    statement = statement.offset(skip).limit(limit).order_by(desc(Note.created_at))
    return db.execute(statement).scalars().all()


def update_note(
        db: Session,
        note: Note,
        note_data: NoteUpdate,
        word_ids: Optional[List[int]] = None,
        relation_ids: Optional[List[int]] = None
) -> Note:
    """更新笔记及其关联"""
    note_data_dict = note_data.dict(exclude_unset=True)

    for field, value in note_data_dict.items():
        setattr(note, field, value)

    # 更新关联单词
    if word_ids is not None:
        # 删除现有关联
        delete_statement = NoteWordLink.__table__.delete().where(NoteWordLink.note_id == note.id)
        db.execute(delete_statement)
        # 添加新关联
        for word_id in word_ids:
            note_word_link = NoteWordLink(note_id=note.id, word_id=word_id)
            db.add(note_word_link)

    # 更新关联关系
    if relation_ids is not None:
        # 删除现有关联
        delete_statement = NoteRelationLink.__table__.delete().where(NoteRelationLink.note_id == note.id)
        db.execute(delete_statement)
        # 添加新关联
        for relation_id in relation_ids:
            note_relation_link = NoteRelationLink(note_id=note.id, relation_id=relation_id)
            db.add(note_relation_link)

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: Note) -> bool:
    """删除笔记及其关联"""
    try:
        # 删除单词关联
        delete_statement = NoteWordLink.__table__.delete().where(NoteWordLink.note_id == note.id)
        db.execute(delete_statement)
        # 删除关系关联
        delete_statement = NoteRelationLink.__table__.delete().where(NoteRelationLink.note_id == note.id)
        db.execute(delete_statement)
        # 删除收藏关联
        delete_statement = UserNoteCollectionLink.__table__.delete().where(UserNoteCollectionLink.note_id == note.id)
        db.execute(delete_statement)
        # 删除笔记
        db.delete(note)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def increment_note_views(db: Session, note: Note) -> Note:
    """增加笔记浏览量"""
    note.views += 1
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def toggle_note_like(db: Session, note: Note) -> Note:
    """切换笔记点赞状态"""
    note.likes += 1
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def collect_note(db: Session, note_id: int, user_id: int) -> bool:
    """收藏笔记（只允许收藏公开笔记）"""
    note = get_note(db, note_id)

    # 只能收藏公开笔记
    if not note or note.visibility != NoteVisibility.PUBLIC:
        return False

    # 检查是否已收藏
    existing_statement = select(UserNoteCollectionLink).where(
        and_(
            UserNoteCollectionLink.user_id == user_id,
            UserNoteCollectionLink.note_id == note_id
        )
    )
    existing = db.execute(existing_statement).scalars().first()

    if existing:
        return False  # 已经收藏过了

    # 添加收藏
    collection = UserNoteCollectionLink(
        user_id=user_id,
        note_id=note_id
    )
    db.add(collection)

    # 更新收藏计数
    note.collect_count += 1
    db.add(note)

    db.commit()
    return True


def uncollect_note(db: Session, note_id: int, user_id: int) -> bool:
    """取消收藏笔记"""
    # 查找收藏记录
    collection_statement = select(UserNoteCollectionLink).where(
        and_(
            UserNoteCollectionLink.user_id == user_id,
            UserNoteCollectionLink.note_id == note_id
        )
    )
    collection = db.execute(collection_statement).scalars().first()

    if not collection:
        return False  # 没有收藏记录

    # 删除收藏
    db.delete(collection)

    # 更新收藏计数
    note = get_note(db, note_id)
    if note and note.collect_count > 0:
        note.collect_count -= 1
        db.add(note)

    db.commit()
    return True


def check_note_collected(db: Session, note_id: int, user_id: int) -> bool:
    """检查用户是否收藏了笔记"""
    collection_statement = select(UserNoteCollectionLink).where(
        and_(
            UserNoteCollectionLink.user_id == user_id,
            UserNoteCollectionLink.note_id == note_id
        )
    )
    collection = db.execute(collection_statement).scalars().first()
    return collection is not None


def get_note_words(db: Session, note_id: int) -> List[int]:
    """获取笔记关联的单词ID列表"""
    statement = select(NoteWordLink.word_id).where(NoteWordLink.note_id == note_id)
    return db.execute(statement).scalars().all()


def get_note_relations(db: Session, note_id: int) -> List[int]:
    """获取笔记关联的关系ID列表"""
    statement = select(NoteRelationLink.relation_id).where(NoteRelationLink.note_id == note_id)
    return db.execute(statement).scalars().all()


def search_notes(
        db: Session,
        keyword: str,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
) -> List[Note]:
    """搜索笔记（考虑可见性）"""
    if user_id:
        # 用户登录：搜索公开笔记和用户自己的私有笔记
        statement = select(Note).where(
            and_(
                or_(
                    Note.title.ilike(f"%{keyword}%"),
                    Note.content.ilike(f"%{keyword}%")
                ),
                or_(
                    Note.visibility == NoteVisibility.PUBLIC,
                    Note.creator_id == user_id
                )
            )
        )
    else:
        # 未登录用户：只搜索公开笔记
        statement = select(Note).where(
            and_(
                or_(
                    Note.title.ilike(f"%{keyword}%"),
                    Note.content.ilike(f"%{keyword}%")
                ),
                Note.visibility == NoteVisibility.PUBLIC
            )
        )

    statement = statement.offset(skip).limit(limit).order_by(desc(Note.created_at))
    return db.execute(statement).scalars().all()
