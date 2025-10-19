# 用户模型
import json
import re

from pydantic import field_validator, model_validator
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime, time
from datetime import date
# 用户相关表
from app.models.enums import LanguageCode, AccentType, ContributionType, ContributionStatus, UserStatus, AuthProvider
from .note import UserNoteCollectionLink
from .book import UserWordbookCollectionLink, UserRelationBookCollectionLink
if TYPE_CHECKING:
    from .note import Note
    from .book import Wordbook, RelationBook
    from .study import *


class User(SQLModel, table=True):
    """
    用户表-存储系统用户的基本信息
    """
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True, description="用户唯一标识符")
    # 登录信息
    username: str = Field(max_length=50, unique=True, index=True, description="用户名")
    email: str = Field(unique=True, index=True, max_length=100, description="用户邮箱")
    phone: Optional[str] = Field(default=None, max_length=20, index=True, unique=True, description="电话号码")
    qq: Optional[str] = Field(default=None, max_length=20, index=True, unique=True, description="qq号")
    wechat: Optional[str] = Field(default=None, max_length=20, index=True, unique=True, description="wx号")
    # 第三方登录标识
    wechat_unionid: Optional[str] = Field(default=None, max_length=100, unique=True, index=True, description="qq")
    qq_openid: Optional[str] = Field(default=None, max_length=100, unique=True, index=True, description="wx")

    # 密码字段（邮箱/手机登录时需要）
    hashed_password: str = Field(default=None, max_length=255, description="加密后的密码")

    # 用户信息字段
    display_name: Optional[str] = Field(default=None, max_length=50, description="用户显示名称")
    avatar: Optional[str] = Field(default=None, max_length=255, description="用户头像URL或路径")

    # 状态与权限字段
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_premium: bool = Field(default=False, description="是否为高级会员")
    is_admin: bool = Field(default=False, description="是否为管理员")

    # 认证相关信息
    auth_provider: AuthProvider = Field(default=AuthProvider.EMAIL)
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)

    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow, description="账户创建时间，默认当前时间")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="账户更新时间，自动更新")
    last_login: Optional[datetime] = Field(default=None, description="最后登录时间")
    # 词库和关系库相关关系
    wordbooks_rel: List["Wordbook"] = Relationship(back_populates="creator_rel")
    collected_wordbooks_rel: List["Wordbook"] = Relationship(
        back_populates="collections_rel",
        link_model=UserWordbookCollectionLink
    )

    # 关系库关系
    relation_books_rel: List["RelationBook"] = Relationship(back_populates="creator_rel")
    collected_relation_books_rel: List["RelationBook"] = Relationship(
        back_populates="collections_rel",
        link_model=UserRelationBookCollectionLink
    )
    # 笔记相关关系
    created_notes_rel: List["Note"] = Relationship(back_populates="creator_rel")
    collected_notes_rel: List["Note"] = Relationship(
        back_populates="collected_by_rel",
        link_model=UserNoteCollectionLink
    )
    # 学习相关关系
    learning_plans_rel: List["UserLearningPlan"] = Relationship(back_populates="user_rel")
    daily_tasks_rel: List["UserDailyTask"] = Relationship(back_populates="user_rel")
    study_sessions_rel: List["UserStudySession"] = Relationship(back_populates="user_rel")
    study_records_rel: List["UserStudyRecord"] = Relationship(back_populates="user_rel")
    word_progress_rel: List["UserWordProgress"] = Relationship(back_populates="user_rel")
    learning_setting_rel: Optional["UserLearningSetting"] = Relationship(back_populates="user_rel")
    study_statistics_rel: List["UserStudyStatistics"] = Relationship(back_populates="user_rel")

    # 用户相关关系
    contributions_rel: List["UserContribution"] = Relationship(
        back_populates="user_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[UserContribution.user_id]"
        }
    )

    reviewed_contributions_rel: List["UserContribution"] = Relationship(
        back_populates="reviewer_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[UserContribution.reviewed_by]"
        }
    )
    statistics_rel: List["UserStatistic"] = Relationship(
        back_populates="user_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[UserStatistic.user_id]"
        })
    setting_rel: "UserSetting" = Relationship(back_populates="user_rel")

    # Pydantic验证器
    # 修正后的验证器
    # 邮箱格式验证
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r'^[a-zA-Z\d._%+-]+@[a-zA-Z\d.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('邮箱格式无效')
        return v

    # 手机号格式验证
    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = re.sub(r'(?!^\+)\D', '', v)
        if not re.match(r'^\+?\d{10,15}$', cleaned):
            raise ValueError('电话号码格式无效')
        return cleaned

        # 模型级验证：检查至少有一个标识

    @model_validator(mode='after')
    @classmethod
    def validate_at_least_one_identifier(cls, values: Any) -> Any:
        """验证至少有一种登录标识"""
        # values 是整个模型的数据字典
        if isinstance(values, dict):
            data = values
        else:
            data = values.model_dump()

        # 检查是否所有标识都为空
        if all(data.get(field) is None for field in ['email', 'phone', 'wechat_unionid', 'qq_openid']):
            raise ValueError("必须提供至少一种登录方式（邮箱、手机、微信或QQ）")
        return values


    @field_validator('display_name')
    @classmethod
    def validate_display_name_content(cls, v: str) -> str:
        """额外的用户名验证"""
        if v.lower() in ['admin', 'root', 'system', 'administrator']:
            raise ValueError('该用户名被保留，不可使用')
        return v


class UserSetting(SQLModel, table=True):
    """
    用户设置表 - 存储用户的个性化学习设置
    对应数据库表: user_settings
    """
    __tablename__ = "user_settings"
    id: Optional[int] = Field(default=None, primary_key=True, description="用户设置id")
    user_id: int = Field(foreign_key="users.id", unique=True, index=True, description="关联用户ID")

    # 学习目标设置
    study_daily_goal: int = Field(default=20, ge=1, le=1000, description="每日学习目标单词数量")
    review_daily_goal: int = Field(default=30, ge=1, le=1000, description="每日复习目标单词数量")

    # 通知设置
    notification_enabled: bool = Field(default=True, description="是否启用通知")
    notification_time: Optional[time] = Field(default=None, description="通知时间")
    study_reminders: bool = Field(default=True, description="是否启用学习提醒")

    # 界面语言与发音设置
    language: LanguageCode = Field(default=LanguageCode.ZH_CN, description="界面语言")
    pronunciation_accent: AccentType = Field(default=AccentType.US, description="发音口音偏好")

    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    user_rel: User = Relationship(back_populates="setting_rel")

    @field_validator('notification_time')
    @classmethod
    def validate_notification_time(cls, v):
        """验证通知时间格式"""
        if v is not None and not isinstance(v, time):
            raise ValueError('通知时间必须是有效的时间对象')
        return v


class UserStatistic(SQLModel, table=True):
    """
    用户统计表，存储用户每日学习统计数据
    对应数据库表: user_settings
    """
    __tablename__ = "user_statistics"
    id: Optional[int] = Field(default=None, primary_key=True, description="统计记录唯一标识符")
    user_id: int = Field(foreign_key="users.id", index=True, description="关联的用户ID")
    date_time: date = Field(default_factory=date.today, description="统计日期")

    # 学习数据
    words_studied: int = Field(default=0, ge=0, description="当日学习的单词数量")
    words_reviewed: int = Field(default=0, ge=0, description="当日复习的单词数量")
    time_studied: int = Field(default=0, ge=0, description="当日学习时长(分钟)")
    review_time: int = Field(default=0, ge=0, description="当日复习时长(分钟)")
    correct_answers: int = Field(default=0, ge=0, description="当日正确答题数量")
    incorrect_answers: int = Field(default=0, ge=0, description="当日错误答题数量")

    # 计算字段（可选，可以根据需要存储或动态计算）
    total_study_time: int = Field(default=0, ge=0, description="总学习时长(分钟)")
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="当日答题正确率")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="记录创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="记录更新时间"
    )

    # 关系
    user_rel: "User" = Relationship(back_populates="statistics_rel")

    # Pydantic验证器
    @field_validator('accuracy_rate')
    @classmethod
    def validate_accuracy_rate(cls, v):
        """验证正确率范围"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('正确率必须在0.0到1.0之间')
        return round(v, 2)  # 保留两位小数

    @field_validator('date_time')
    @classmethod
    def validate_date_not_future(cls, v):
        """验证日期不能是未来日期"""
        if v > date.today():
            raise ValueError('统计日期不能是未来日期')
        return v

    # 计算方法
    def calculate_accuracy(self):
        """计算正确率"""
        total = self.correct_answers + self.incorrect_answers
        if total > 0:
            self.accuracy_rate = round(self.correct_answers / total, 2)
        else:
            self.accuracy_rate = 0.0
        return self.accuracy_rate

    def calculate_total_study_time(self):
        """计算总学习时间"""
        self.total_study_time = self.time_studied + self.review_time
        return self.total_study_time


class UserContribution(SQLModel, table=True):
    """统一用户贡献表"""
    __tablename__ = "user_contributions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", description="提交用户ID")
    contribution_type: ContributionType = Field(description="贡献类型")

    # 目标表信息
    target_table: str = Field(description="目标表名")
    target_id: Optional[int] = Field(default=None, description="目标记录ID（更新时使用）")

    # 提交的数据（JSON格式）
    data: str = Field(description="提交的数据（JSON格式）")

    # 审核信息
    status: ContributionStatus = Field(default=ContributionStatus.PENDING, description="审核状态")
    reviewed_by: Optional[int] = Field(default=None, foreign_key="users.id", description="审核人ID")
    reviewed_at: Optional[datetime] = Field(default=None, description="审核时间")
    review_feedback: Optional[str] = Field(default=None, description="审核反馈")

    # 统计信息
    likes: int = Field(default=0, description="点赞数")
    reports: int = Field(default=0, description="举报数")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # 关系定义
    user_rel: "User" = Relationship(
        back_populates="contributions_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[UserContribution.user_id]"
        }
    )

    reviewer_rel: Optional["User"] = Relationship(
        back_populates="reviewed_contributions_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[UserContribution.reviewed_by]"
        }
    )
    # 关系
    # user: "User" = Relationship(back_populates="contributions")
    # reviewer: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "UserContribution.reviewed_by"})

    # 辅助方法
    def get_data_dict(self) -> Dict[str, Any]:
        """获取解析后的数据"""
        return json.loads(self.data)

    def set_data_dict(self, data_dict: Dict[str, Any]):
        """设置数据字典"""
        self.data = json.dumps(data_dict, ensure_ascii=False)