from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from pydantic import field_validator, ValidationInfo
from .enums import RelationCategory, RelationType
from sqlalchemy import Column, Integer, ForeignKey
from .note import NoteRelationLink
from .book import RelationBookRelationLink
if TYPE_CHECKING:
    from .word import Word
    from .note import Note
    from .book import RelationBook


class WordRelation(SQLModel, table=True):
    """
    单词关系表
    存储单词之间的关系
    """
    __tablename__ = "word_relations"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_word_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("words.id", ondelete="CASCADE")
        )
    )
    target_word_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("words.id", ondelete="CASCADE")
        )
    )
    strength: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="关系强度"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="关系更新时间"
    )
    title: Optional[str] = Field(default=None, max_length=50, description="关系标题")
    description: str = Field(default="", max_length=500, description="关系描述")

    # 关系定义
    source_word_rel: "Word" = Relationship(
        back_populates="source_relations_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[WordRelation.source_word_id]",
            "lazy": "selectin"
        }
    )

    target_word_rel: "Word" = Relationship(
        back_populates="target_relations_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[WordRelation.target_word_id]",
            "lazy": "selectin"
        }
    )

    # 关系类型 - 一对多关系，配置正确
    relation_type_rel: List["RelationType"] = Relationship(
        back_populates="word_relations_rel",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        })

    # 笔记相关关系 - 多对多，不能在Relationship中配置cascade
    notes_rel: List["Note"] = Relationship(
        back_populates="relations_rel",
        link_model=NoteRelationLink
    )

    # 关系库相关关系 - 多对多，不能在Relationship中配置cascade
    relation_books_rel: List["RelationBook"] = Relationship(
        back_populates="relations_rel",
        link_model=RelationBookRelationLink
    )

    @field_validator('source_word_id', 'target_word_id')
    @classmethod
    def validate_word_ids(cls, value: int, info: ValidationInfo):
        """验证单词ID不能相同"""
        field_name = info.field_name

        # 根据当前验证的字段确定要比较的另一个字段
        if field_name == 'source_word_id':
            other_field = 'target_word_id'
        else:
            other_field = 'source_word_id'

        # 检查另一个字段的值
        if other_field in info.data and value == info.data[other_field]:
            raise ValueError("源单词和目标单词不能相同")

        return value


class RelationType(SQLModel, table=True):
    """
    关系类型定义表
    存储可复用的关系类型定义
    """
    __tablename__ = "relation_types"

    id: Optional[int] = Field(default=None, primary_key=True, description="关系类型唯一标识符")
    relation_id: int = Field(
        foreign_key="word_relations.id",
        description="关系id",
    )
    category: RelationCategory = Field(description="关系类别")
    type_name: RelationType = Field(description="关系类型名称")
    title: Optional[str] = Field(default=None, max_length=50, description="关系类型标题")
    description: Optional[str] = Field(default=None, max_length=500, description="关系类型描述")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 一对多关系
    word_relations_rel: "WordRelation" = Relationship(back_populates="relation_type_rel")