# app/schemas/word_relation.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.models.enums import AccentType, PartOfSpeechAbbr, TagType, FormType


# 基础Schemas
class WordDefinitionBase(BaseModel):
    part_of_speech: PartOfSpeechAbbr
    definition: str
    definition_cn: str
    order: int = Field(ge=1, default=1)
    domains_json: Optional[str] = None
    example_usage: Optional[str] = None


class ExampleBase(BaseModel):
    sentence: str
    translation: str
    source: Optional[str] = None
    context: Optional[str] = None


class WordFormBase(BaseModel):
    form_type: FormType
    form_word: str


class WordPronunciationBase(BaseModel):
    accent: AccentType
    audio_url: str
    phonetic: str
    voice_actor: Optional[str] = None
    audio_quality: Optional[str] = None


# 创建Schemas
class WordDefinitionCreate(WordDefinitionBase):
    pass


class ExampleCreate(ExampleBase):
    pass


class WordFormCreate(WordFormBase):
    pass


class WordPronunciationCreate(WordPronunciationBase):
    pass


# 更新Schemas
class WordDefinitionUpdate(BaseModel):
    part_of_speech: Optional[PartOfSpeechAbbr] = None
    definition: Optional[str] = None
    definition_cn: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    domains_json: Optional[str] = None
    example_usage: Optional[str] = None


class ExampleUpdate(BaseModel):
    sentence: Optional[str] = None
    translation: Optional[str] = None
    source: Optional[str] = None
    context: Optional[str] = None


class WordFormUpdate(BaseModel):
    form_type: Optional[str] = None
    form_word: Optional[str] = None


class WordPronunciationUpdate(BaseModel):
    accent: Optional[AccentType] = None
    audio_url: Optional[str] = None
    phonetic: Optional[str] = None
    voice_actor: Optional[str] = None
    audio_quality: Optional[str] = None


# 读取Schemas
class WordDefinitionRead(WordDefinitionBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExampleRead(ExampleBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordFormRead(WordFormBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordPronunciationRead(WordPronunciationBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagRead(BaseModel):
    id: int
    name: str
    type: TagType
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



# 单词的Schemas保持不变...
