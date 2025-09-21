# 用户模型
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, time
from datetime import date

# 用户相关表
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="用户唯一标识符")
    username: str = Field(unique=True, index=True, description="用户名，用于登录和显示")
    email: str = Field(unique=True, index=True, description="用户邮箱，用于登录和通知")
    hashed_password: str = Field(description="加密后的密码")
    display_name: Optional[str] = Field(default=None, description="用户显示名称，可不同于用户名")
    avatar: Optional[str] = Field(default=None, description="用户头像URL或路径")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="账户创建时间")
    last_login: Optional[datetime] = Field(default=None, description="最后登录时间")
    is_active: bool = Field(default=True, description="账户是否激活")
    is_premium: bool = Field(default=False, description="是否为高级会员")
    streak_days: int = Field(default=0, description="连续学习天数")
    total_words_learned: int = Field(default=0, description="已学习的单词总数")

    # 关系
    settings: Optional["UserSetting"] = Relationship(back_populates="user")
    statistics: List["UserStatistic"] = Relationship(back_populates="user")
    word_lists: List["WordList"] = Relationship(back_populates="user")
    study_plans: List["StudyPlan"] = Relationship(back_populates="user")
    progress: List["UserWordProgress"] = Relationship(back_populates="user")
    sessions: List["StudySession"] = Relationship(back_populates="user")
    reviews: List["ReviewSchedule"] = Relationship(back_populates="user")
    quiz_attempts: List["QuizAttempt"] = Relationship(back_populates="user")
    # 明确指定使用 submitted_by 外键
    contributions: List["UserContribution"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "UserContribution.submitted_by"}
    )


class UserSetting(SQLModel, table=True):
    """用户设置表，存储用户的个性化学习设置"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="关联用户ID")
    daily_goal: int = Field(default=20, description="每日学习目标单词数")
    notification_enabled: bool = Field(default=True, description="是否启用通知")
    notification_time: Optional[time] = Field(default=None, description="通知时间")
    study_reminders: bool = Field(default=True, description="是否启用学习提醒")
    language: str = Field(default="zh-CN", description="界面语言")
    pronunciation_accent: str = Field(default="us", description="发音口音偏好")

    # 关系
    user: User = Relationship(back_populates="settings")


class UserStatistic(SQLModel, table=True):
    """用户统计表，存储用户每日学习统计数据"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="关联用户ID")
    dates: date = Field(default_factory=date.today, description="统计日期")
    words_studied: int = Field(default=0, description="当日学习单词数")
    time_studied: int = Field(default=0, description="当日学习时间（分钟）")
    correct_answers: int = Field(default=0, description="当日正确回答数")
    incorrect_answers: int = Field(default=0, description="当日错误回答数")

    # 关系
    user: User = Relationship(back_populates="statistics")