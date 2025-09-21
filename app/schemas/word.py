# schemas/word.py
import json
import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator, validator
from enum import Enum


# 枚举定义
class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    PRONOUN = "pronoun"
    INTERJECTION = "interjection"
    DETERMINER = "determiner"
    PHRASAL_VERB = "phrasal_verb"
    IDIOM = "idiom"


class FormType(str, Enum):
    PLURAL = "plural"
    PAST_TENSE = "past_tense"
    PAST_PARTICIPLE = "past_participle"
    PRESENT_PARTICIPLE = "present_participl"
    THIRD_PERSON_SINGULAR = "third_person_singular"
    COMPARATIVE = "comparative"
    SUPERLATIVE = "superlative"
    BASE_FORM = "base_form"


class AccentType(str, Enum):
    US = "us"
    UK = "uk"
    AU = "au"
    CA = "ca"


class RelationType(str, Enum):
    SYNONYM = "synonym"
    ANTONYM = "antonym"
    DERIVATIVE = "derivative"
    HYPERNYM = "hypernym"
    HYPONYM = "hyponym"
    HOLONYM = "holonym"
    MERONYM = "meronym"


# 基础模型
class WordBase(BaseModel):
    word: str
    normalized_word: str
    length: int = 0
    frequency_rank: Optional[int] = None
    difficulty_level_id: int = 1
    is_common: bool = True
    tags: Optional[List[str]] = None
    etymology: Optional[str] = None
    description: str = ""

    @field_validator('word')
    def word_must_be_english_only(cls, v):
        # ✅ 允许：英文字母、空格、撇号、连字符
        if not re.fullmatch(r"^[a-zA-Z\s'-]+$", v):
            raise ValueError("word 只能包含英文字母（a-z, A-Z）、空格、撇号 (') 或连字符 (-)")
        return v

# 创建模型
class WordCreate(WordBase):
    pass


# 更新模型
class WordUpdate(BaseModel):
    word: Optional[str] = None
    normalized_word: Optional[str] = None
    length: Optional[int] = None
    frequency_rank: Optional[int] = None
    difficulty_level_id: Optional[int] = None
    is_common: Optional[bool] = None
    tags: Optional[List[str]] = None
    etymology: Optional[str] = None
    description: str = ""

# 响应模型
class WordRead(WordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

        # 添加自定义验证器来处理tags字段
        @field_validator('tags', mode='before')
        @classmethod
        def validate_tags(cls, v):
            if isinstance(v, str):
                # 如果是从数据库读取的JSON字符串，则解析它
                return json.loads(v)
            return v


# 释义模型
class WordDefinitionBase(BaseModel):
    part_of_speech: PartOfSpeech
    definition: str
    definition_cn: str
    order: int = 0
    domains: Optional[List[str]] = None
    example_usage: Optional[str] = None


class WordDefinitionCreate(WordDefinitionBase):
    word_id: int


class WordDefinitionRead(WordDefinitionBase):
    id: int
    word_id: int

    class Config:
        from_attributes = True


class WordDefinitionUpdate(WordDefinitionBase):
    pass


# 例句模型
class ExampleBase(BaseModel):
    sentence: str
    translation: str
    source: Optional[str] = None
    context: Optional[str] = None


class ExampleCreate(ExampleBase):
    word_id: int


class ExampleRead(ExampleBase):
    id: int
    word_id: int

    class Config:
        from_attributes = True


class ExampleUpdate(ExampleBase):
    pass


# 词形变化模型
class WordFormBase(BaseModel):
    form_type: FormType
    form_word: str
    is_standard: bool = True


class WordFormCreate(WordFormBase):
    word_id: int


class WordFormRead(WordFormBase):
    id: int
    word_id: int

    class Config:
        from_attributes = True


class WordFormUpdate(WordFormBase):
    pass


# 发音模型
class WordPronunciationBase(BaseModel):
    accent: AccentType
    audio_url: str
    phonetic: Optional[str] = None
    voice_actor: Optional[str] = None
    audio_quality: Optional[str] = None


class WordPronunciationCreate(WordPronunciationBase):
    word_id: int


class WordPronunciationRead(WordPronunciationBase):
    id: int
    word_id: int

    class Config:
        from_attributes = True


class WordPronunciationUpdate(WordPronunciationBase):
    pass


# 关系模型
class WordRelationBase(BaseModel):
    relation_type: RelationType
    strength: Optional[float] = 1.0
    created_at: datetime
    description: str = ""

class WordRelationCreate(BaseModel):
    source_id: int
    target_id: int
    relation_type: RelationType
    strength: Optional[float] = 1.0


class WordRelationRead(WordRelationBase):
    id: int
    source_id: int
    target_id: int

    class Config:
        from_attributes = True


class WordRelationUpdate(WordRelationBase):
    pass


class GraphPath(BaseModel):
    """表示两个单词之间的路径"""
    path: List[int]  # 单词ID的列表，表示路径
    relations: List[Optional[int]]  # 关系ID的列表，表示路径上的关系
    length: int  # 路径长度

    class Config:
        from_attributes = True
