from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date


class WordList(SQLModel, table=True):
    """单词列表表，存储用户创建的单词列表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="创建者用户ID")
    name: str = Field(description="列表名称")
    description: Optional[str] = Field(default=None, description="列表描述")
    is_public: bool = Field(default=False, description="是否公开")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    word_count: int = Field(default=0, description="单词数量")

    # 关系
    user: "User" = Relationship(back_populates="word_lists")
    items: List["WordListItem"] = Relationship(back_populates="word_list")
    study_plans: List["StudyPlan"] = Relationship(back_populates="word_list")


class WordListItem(SQLModel, table=True):
    """单词列表项表，存储单词列表中的单词"""
    id: Optional[int] = Field(default=None, primary_key=True)
    word_list_id: int = Field(foreign_key="wordlist.id", description="关联单词列表ID")
    word_id: int = Field(foreign_key="word.id", description="关联单词ID")
    added_at: datetime = Field(default_factory=datetime.utcnow, description="添加时间")
    order: int = Field(default=0, description="排序顺序")

    # 关系
    word_list: WordList = Relationship(back_populates="items")
    word: "Word" = Relationship(back_populates="list_items")


class StudyPlan(SQLModel, table=True):
    """学习计划表，存储用户的学习计划"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="创建者用户ID")
    name: str = Field(description="计划名称")
    description: Optional[str] = Field(default=None, description="计划描述")
    word_list_id: int = Field(foreign_key="wordlist.id", description="关联单词列表ID")
    daily_target: int = Field(default=10, description="每日目标单词数")
    start_date: date = Field(description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    is_active: bool = Field(default=True, description="是否激活")

    # 关系
    user: "User" = Relationship(back_populates="study_plans")
    word_list: WordList = Relationship(back_populates="study_plans")


class UserWordProgress(SQLModel, table=True):
    """用户单词进度表，存储用户对每个单词的学习进度"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="用户ID")
    word_id: int = Field(foreign_key="word.id", description="单词ID")
    status: str = Field(default="new", description="学习状态")
    familiarity: int = Field(default=0, description="熟悉程度")
    last_studied: Optional[datetime] = Field(default=None, description="最后学习时间")
    next_review: Optional[datetime] = Field(default=None, description="下次复习时间")
    study_count: int = Field(default=0, description="学习次数")
    correct_count: int = Field(default=0, description="正确次数")
    wrong_count: int = Field(default=0, description="错误次数")
    ease_factor: float = Field(default=2.5, description="简易因子（用于间隔重复算法）")
    interval: int = Field(default=0, description="间隔天数")
    due_date: Optional[datetime] = Field(default=None, description="到期日期")

    # 关系
    user: "User" = Relationship(back_populates="progress")
    word: "Word" = Relationship(back_populates="progress")


class StudySession(SQLModel, table=True):
    """学习会话表，存储用户的学习会话记录"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="用户ID")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration: int = Field(default=0, description="持续时间（秒）")
    words_studied: int = Field(default=0, description="学习单词数")
    session_type: str = Field(description="会话类型")

    # 关系
    user: "User" = Relationship(back_populates="sessions")


class ReviewSchedule(SQLModel, table=True):
    """复习计划表，存储用户的单词复习计划"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="用户ID")
    word_id: int = Field(foreign_key="word.id", description="单词ID")
    due_date: datetime = Field(description="到期日期")
    completed: bool = Field(default=False, description="是否已完成")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")

    # 关系
    user: "User" = Relationship(back_populates="reviews")
    word: "Word" = Relationship(back_populates="reviews")