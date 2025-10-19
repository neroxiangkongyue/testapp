from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime


# ===== 基础 Schema =====
class UserBrief(SQLModel):
    """用户简要信息"""
    id: int
    display_name: str
    avatar: Optional[str] = None


class WordBrief(SQLModel):
    """单词简要信息"""
    id: int
    word: str
    normalized_word: str
    length: int


class WordRelationBrief(SQLModel):
    """关系简要信息"""
    id: int
    source_word_id: int
    target_word_id: int
    strength: float
    description: str
    created_at: datetime


# ===== 词库相关 Schema =====
class WordbookBase(SQLModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    cover_image: Optional[str] = None


class WordbookCreate(WordbookBase):
    pass


class WordbookUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_image: Optional[str] = None


class WordbookBrief(WordbookBase):
    id: int
    creator_id: int
    word_count: int
    created_at: datetime
    updated_at: datetime


class Wordbook(WordbookBrief):
    creator: UserBrief


class WordbookWithWords(Wordbook):
    words: List[WordBrief] = []
    is_collected: bool = False


class WordbookWordLinkCreate(SQLModel):
    word_id: int
    order: int = 0
    note: Optional[str] = None


# ===== 关系库相关 Schema =====
class RelationBookBase(SQLModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    cover_image: Optional[str] = None


class RelationBookCreate(RelationBookBase):
    pass


class RelationBookUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_image: Optional[str] = None


class RelationBookBrief(RelationBookBase):
    id: int
    creator_id: int
    relation_count: int
    created_at: datetime
    updated_at: datetime


class RelationBook(RelationBookBrief):
    creator: UserBrief


class RelationBookWithRelations(RelationBook):
    relations: List[WordRelationBrief] = []
    is_collected: bool = False


class RelationBookRelationLinkCreate(SQLModel):
    relation_id: int
    order: int = 0
    note: Optional[str] = None
