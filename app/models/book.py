from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey


if TYPE_CHECKING:
    from .user import User
    from .word import Word
    from .relation import WordRelation
    from .study import UserLearningPlan


class RelationBookRelationLink(SQLModel, table=True):
    """关系库-关系关联表"""
    __tablename__ = "relation_book_relations_link"

    relation_book_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("relation_books.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="关系库ID"
    )
    relation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("word_relations.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="关系ID"
    )
    added_at: datetime = Field(default_factory=datetime.utcnow, description="添加时间")
    order: int = Field(default=0, description="排序顺序")
    note: Optional[str] = Field(default=None, description="用户备注")


class UserWordbookCollectionLink(SQLModel, table=True):
    """用户-词库收藏关联表"""
    __tablename__ = "user_wordbook_collections_link"

    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="用户ID"
    )
    wordbook_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("wordbooks.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="词库ID"
    )
    collected_at: datetime = Field(default_factory=datetime.utcnow, description="收藏时间")


class UserRelationBookCollectionLink(SQLModel, table=True):
    """用户-关系库收藏关联表"""
    __tablename__ = "user_relation_book_collections_link"

    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="用户ID"
    )
    relation_book_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("relation_books.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="关系库ID"
    )
    collected_at: datetime = Field(default_factory=datetime.utcnow, description="收藏时间")


class WordbookWordLink(SQLModel, table=True):
    """词库-单词关联表"""
    __tablename__ = "wordbook_words_link"

    wordbook_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("wordbooks.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="词库ID"
    )
    word_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("words.id", ondelete="CASCADE"),
            primary_key=True
        ),
        description="单词ID"
    )
    added_at: datetime = Field(default_factory=datetime.utcnow, description="添加时间")
    order: int = Field(default=0, description="排序顺序")
    note: Optional[str] = Field(default=None, description="用户备注")


class Wordbook(SQLModel, table=True):
    """词库表，用户可以创建自己的词库"""
    __tablename__ = "wordbooks"

    id: Optional[int] = Field(default=None, primary_key=True, description="词库ID")
    name: str = Field(max_length=100, description="词库名称")
    creator_id: int = Field(
        foreign_key="users.id",
        description="创建者ID"
    )
    description: Optional[str] = Field(default=None, description="词库描述")
    is_public: bool = Field(default=False, description="是否公开")
    word_count: int = Field(default=0, description="单词数量")
    cover_image: Optional[str] = Field(default=None, description="封面图片URL")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系定义
    creator_rel: Optional["User"] = Relationship(back_populates="wordbooks_rel")
    words_rel: List["Word"] = Relationship(
        back_populates="wordbooks_rel",
        link_model=WordbookWordLink
    )
    collections_rel: List["User"] = Relationship(
        back_populates="collected_wordbooks_rel",
        link_model=UserWordbookCollectionLink
    )
    # 学习计划关系
    learning_plans_rel: List["UserLearningPlan"] = Relationship(back_populates="wordbook_rel")


class RelationBook(SQLModel, table=True):
    """关系库表，用户可以创建自己的关系库"""
    __tablename__ = "relation_books"

    id: Optional[int] = Field(default=None, primary_key=True, description="关系库ID")
    name: str = Field(max_length=100, description="关系库名称")
    creator_id: int = Field(
        foreign_key="users.id",
        description="创建者ID"
    )
    description: Optional[str] = Field(default=None, description="关系库描述")
    is_public: bool = Field(default=False, description="是否公开")
    relation_count: int = Field(default=0, description="关系数量")
    cover_image: Optional[str] = Field(default=None, description="封面图片URL")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系定义
    creator_rel: Optional["User"] = Relationship(back_populates="relation_books_rel")
    relations_rel: List["WordRelation"] = Relationship(
        back_populates="relation_books_rel",
        link_model=RelationBookRelationLink
    )
    collections_rel: List["User"] = Relationship(
        back_populates="collected_relation_books_rel",
        link_model=UserRelationBookCollectionLink
    )
