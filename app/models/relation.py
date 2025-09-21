from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from .enums import RelationType

if TYPE_CHECKING:
    from .word import Word
    from .content import Tag, Category


class WordRelation(SQLModel, table=True):
    """单词关系表，存储单词之间的语义关系"""
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="word.id", description="源单词ID")
    target_id: int = Field(foreign_key="word.id", description="目标单词ID")
    relation_type: RelationType = Field(description="关系类型")
    strength: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="关系强度")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    description: str = Field(default="", description="关系描述")

    # 关系
    source_word: "Word" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[WordRelation.source_id]",
            "primaryjoin": "WordRelation.source_id == Word.id"
        },
        back_populates="outgoing_relations"
    )
    target_word: "Word" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[WordRelation.target_id]",
            "primaryjoin": "WordRelation.target_id == Word.id"
        },
        back_populates="incoming_relations"
    )


class WordTag(SQLModel, table=True):
    """单词标签关联表，建立单词和标签的多对多关系"""
    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="word.id", description="关联单词ID")
    tag_id: int = Field(foreign_key="tag.id", description="关联标签ID")

    # 关系
    word: "Word" = Relationship(back_populates="tags")
    tag: "Tag" = Relationship(back_populates="words")


class WordCategory(SQLModel, table=True):
    """单词分类关联表，建立单词和分类的多对多关系"""
    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="word.id", description="关联单词ID")
    category_id: int = Field(foreign_key="category.id", description="关联分类ID")

    # 关系
    word: "Word" = Relationship(back_populates="categories")
    category: "Category" = Relationship(back_populates="words")
