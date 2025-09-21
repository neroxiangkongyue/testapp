# models/word.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import json
from sqlalchemy import Column, Text
from app.models.enums import PartOfSpeech, FormType, AccentType

if TYPE_CHECKING:
    from .content import DifficultyLevel
    from .relation import WordRelation, WordTag, WordCategory
    from .study import WordListItem, UserWordProgress, ReviewSchedule


# 单词核心表
class Word(SQLModel, table=True):
    """单词表，存储单词的基本信息"""
    id: Optional[int] = Field(default=None, primary_key=True, description="单词唯一标识符")
    word: str = Field(index=True, description="单词原文")
    normalized_word: str = Field(index=True, unique=True, description="标准化后的单词(小写形式，便于搜索)")
    length: int = Field(default=0, description="单词长度(字符数)")
    frequency_rank: Optional[int] = Field(default=None, description="词频排名，数值越小表示越常见")
    difficulty_level_id: int = Field(foreign_key="difficultylevel.id", description="关联的难度等级ID")
    is_common: bool = Field(default=True, description="是否为常用词")
    tags_json: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="单词标签的JSON字符串"
    )
    etymology: Optional[str] = Field(default=None, description="词源信息")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="单词添加时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="单词最后更新时间")
    description: str = Field(default="", description="描述")

    # 关系
    difficulty_level: "DifficultyLevel" = Relationship(back_populates="words")
    definitions: List["WordDefinition"] = Relationship(back_populates="word")
    examples: List["Example"] = Relationship(back_populates="word")
    forms: List["WordForm"] = Relationship(back_populates="word")
    pronunciations: List["WordPronunciation"] = Relationship(back_populates="word")
    outgoing_relations: List["WordRelation"] = Relationship(
        back_populates="source_word",
        sa_relationship_kwargs={"foreign_keys": "WordRelation.source_id"}
    )
    incoming_relations: List["WordRelation"] = Relationship(
        back_populates="target_word",
        sa_relationship_kwargs={"foreign_keys": "WordRelation.target_id"}
    )
    tags: List["WordTag"] = Relationship(back_populates="word")
    categories: List["WordCategory"] = Relationship(back_populates="word")
    list_items: List["WordListItem"] = Relationship(back_populates="word")
    progress: List["UserWordProgress"] = Relationship(back_populates="word")
    reviews: List["ReviewSchedule"] = Relationship(back_populates="word")

    # 属性方法来方便地访问tags
    @property
    def tags_list(self) -> Optional[List[str]]:
        """获取标签列表"""
        if self.tags_json:
            return json.loads(self.tags_json)
        return None

    @tags_list.setter
    def tags_list(self, value: Optional[List[str]]):
        """设置标签列表"""
        if value:
            self.tags_json = json.dumps(value)
        else:
            self.tags_json = None


class WordDefinition(SQLModel, table=True):
    """单词定义表，存储单词的不同词性和定义"""
    id: Optional[int] = Field(default=None, primary_key=True, description="释义唯一标识符")
    word_id: int = Field(foreign_key="word.id", description="关联的单词ID")
    part_of_speech: PartOfSpeech = Field(description="词性")
    definition: str = Field(sa_column=Column(Text), description="英文释义")
    definition_cn: str = Field(sa_column=Column(Text), description="中文释义")
    order: int = Field(default=0, description="释义显示顺序(同一单词可能有多个释义)")
    domains_json: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="适用领域的JSON字符串(如:医学,法律,计算机等)"
    )
    example_usage: Optional[str] = Field(default=None, description="用法示例")

    # 定义关系
    word: Word = Relationship(back_populates="definitions")

    # 属性方法来方便地访问domains
    @property
    def domains(self) -> Optional[List[str]]:
        """获取领域列表"""
        if self.domains_json:
            return json.loads(self.domains_json)
        return None

    @domains.setter
    def domains(self, value: Optional[List[str]]):
        """设置领域列表"""
        if value:
            self.domains_json = json.dumps(value)
        else:
            self.domains_json = None


class Example(SQLModel, table=True):
    """例句表，存储单词的用法例句"""
    id: Optional[int] = Field(default=None, primary_key=True, description="例句唯一标识符")
    word_id: int = Field(foreign_key="word.id", description="关联的单词ID")
    sentence: str = Field(sa_column=Column(Text), description="例句原文")
    translation: str = Field(sa_column=Column(Text), description="例句翻译")
    source: Optional[str] = Field(default=None, description="例句来源(如词典名称、文学作品等)")
    context: Optional[str] = Field(default=None, description="例句上下文信息")

    # 定义关系
    word: Word = Relationship(back_populates="examples")


class WordForm(SQLModel, table=True):
    """单词形式表，存储单词的不同语法形式"""
    id: Optional[int] = Field(default=None, primary_key=True, description="单词形式唯一标识符")
    word_id: int = Field(foreign_key="word.id", description="关联的单词ID")
    form_type: FormType = Field(description="形式类型")
    form_word: str = Field(description="变形后的单词")
    is_standard: bool = Field(default=True, description="是否为标准形式")

    # 定义关系
    word: Word = Relationship(back_populates="forms")


class WordPronunciation(SQLModel, table=True):
    """发音表，存储单词的不同口音发音"""
    id: Optional[int] = Field(default=None, primary_key=True, description="发音记录唯一标识符")
    word_id: int = Field(foreign_key="word.id", description="关联的单词ID")
    accent: AccentType = Field(description="发音口音")
    audio_url: str = Field(description="发音音频文件URL")
    phonetic: Optional[str] = Field(default=None, description="音标表示")
    voice_actor: Optional[str] = Field(default=None, description="配音演员")
    audio_quality: Optional[str] = Field(default=None, description="音频质量(如:标准,高清)")

    # 定义关系
    word: Word = Relationship(back_populates="pronunciations")

