from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.enums import NoteVisibility
from sqlalchemy import Column, Integer, ForeignKey

if TYPE_CHECKING:
    from .user import User
    from .word import Word
    from .relation import WordRelation


class NoteWordLink(SQLModel, table=True):
    """笔记-单词关联表"""
    __tablename__ = "note_words_link"

    note_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("notes.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="笔记ID"
    )
    word_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("words.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="单词ID"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


class NoteRelationLink(SQLModel, table=True):
    """笔记-关系关联表"""
    __tablename__ = "note_relations_link"

    note_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("notes.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="笔记ID"
    )
    relation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("word_relations.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="关系ID"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


class UserNoteCollectionLink(SQLModel, table=True):
    """用户-笔记收藏关联表"""
    __tablename__ = "user_note_collections_link"

    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="用户ID"
    )
    note_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("notes.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="笔记ID"
    )
    collected_at: datetime = Field(default_factory=datetime.utcnow, description="收藏时间")


class Note(SQLModel, table=True):
    """笔记表，用户可以创建关于单词或关系的笔记"""
    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: int = Field(foreign_key="users.id", description="创建者ID")

    # 笔记内容
    title: str = Field(max_length=100, description="笔记标题")
    content: str = Field(description="笔记内容")

    # 统计信息
    likes: int = Field(default=0, description="点赞数")
    views: int = Field(default=0, description="浏览数")
    shares: int = Field(default=0, description="分享次数")
    collect_count: int = Field(default=0, description="收藏次数")

    # 可见性
    visibility: NoteVisibility = Field(default=NoteVisibility.PRIVATE, description="笔记可见性")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系定义
    creator_rel: "User" = Relationship(back_populates="created_notes_rel")
    collected_by_rel: List["User"] = Relationship(
        back_populates="collected_notes_rel",
        link_model=UserNoteCollectionLink
    )
    words_rel: List["Word"] = Relationship(
        back_populates="notes_rel",
        link_model=NoteWordLink
    )
    relations_rel: List["WordRelation"] = Relationship(
        back_populates="notes_rel",
        link_model=NoteRelationLink
    )
