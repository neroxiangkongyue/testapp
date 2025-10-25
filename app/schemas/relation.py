# app/schemas/relation.py
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.models import enums
from app.models.enums import RelationCategory
from app.schemas.note import WordBrief


class WordRelationBase(BaseModel):
    source_word_id: int = Field(..., description="源单词ID")
    target_word_id: int = Field(..., description="目标单词ID")
    strength: Optional[float] = Field(0.8, ge=0.0, le=1.0, description="关系强度")
    title: str = Field(None, max_length=50, description="关系标题")
    description: str = Field(None, max_length=500, description="关系描述")


class WordRelationCreate(WordRelationBase):
    pass


class WordRelationUpdate(BaseModel):
    strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="关系强度")
    description: Optional[str] = Field(None, max_length=500, description="关系描述")


class WordRelationInDBBase(WordRelationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordRelation(WordRelationInDBBase):
    pass


class WordRelationWithWords(WordRelationInDBBase):
    source_word: WordBrief
    target_word: WordBrief
    relation_types: List["RelationType"] = []


class RelationTypeBase(BaseModel):
    relation_id: int = Field(..., description="关联的关系ID")
    type_name: str = Field(..., max_length=50, description="关系类型名称")
    category: RelationCategory = Field(..., description="关系类别")
    description: Optional[str] = Field(None, max_length=500, description="关系类型描述")


class RelationTypeCreate(RelationTypeBase):
    pass


class RelationTypeUpdate(BaseModel):
    category: Optional[RelationCategory] = Field(None, description="关系类别")
    type_name: Optional[enums.RelationType] = Field(None, max_length=50, description="关系类型名称")
    title: Optional[str] = Field(None, max_length=50, description="关系类型描述")
    description: Optional[str] = Field(None, max_length=500, description="关系类型描述")


class RelationType(RelationTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PathNode(BaseModel):
    word_id: int
    word: WordBrief
    relation_id: Optional[int] = None
    relation: Optional["WordRelation"] = None


class PathResponse(BaseModel):
    path: List[PathNode]
    total_strength: float
    length: int


class GraphNode(BaseModel):
    id: int
    word: str
    level: int


class GraphEdge(BaseModel):
    source: int
    target: int
    relation_id: int
    strength: float


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
