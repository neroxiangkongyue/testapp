# app/schemas/note.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import NoteVisibility


class NoteBase(BaseModel):
    title: str = Field(..., max_length=100, description="笔记标题")
    content: str = Field(..., description="笔记内容")
    visibility: NoteVisibility = Field(default=NoteVisibility.PRIVATE, description="笔记可见性")


class NoteCreate(NoteBase):
    word_ids: Optional[List[int]] = Field(default=None, description="关联的单词ID列表")
    relation_ids: Optional[List[int]] = Field(default=None, description="关联的关系ID列表")


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100, description="笔记标题")
    content: Optional[str] = Field(None, description="笔记内容")
    visibility: Optional[NoteVisibility] = Field(None, description="笔记可见性")


class NoteInDBBase(NoteBase):
    id: int
    creator_id: int
    likes: int
    views: int
    shares: int
    collect_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Note(NoteInDBBase):
    pass


# 避免循环导入，先使用字符串类型注解
class NoteWithRelations(NoteInDBBase):
    words: List["WordBrief"] = Field(default_factory=list, description="关联的单词")
    relations: List["RelationBrief"] = Field(default_factory=list, description="关联的关系")
    creator: "UserBrief" = Field(..., description="创建者信息")
    is_collected: bool = Field(default=False, description="当前用户是否收藏")


class NoteBrief(BaseModel):
    id: int
    title: str
    creator_id: int
    visibility: NoteVisibility
    likes: int
    views: int
    created_at: datetime

    class Config:
        from_attributes = True


class WordBrief(BaseModel):
    id: int
    word: str
    normalized_word: str
    length: int

    class Config:
        from_attributes = True


class RelationBrief(BaseModel):
    id: int
    description: str
    strength: Optional[float] = None

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True