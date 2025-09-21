from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from .enums import ContributionType, ContributionStatus


class UserContribution(SQLModel, table=True):
    """用户贡献表，存储用户对单词库的贡献"""
    id: Optional[int] = Field(default=None, primary_key=True)
    type: ContributionType = Field(description="贡献类型")
    data: str = Field(description="贡献数据（JSON格式）")
    status: ContributionStatus = Field(default=ContributionStatus.PENDING, description="审核状态")
    submitted_by: int = Field(foreign_key="user.id", description="提交者用户ID")
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="提交时间")
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id", description="审核者用户ID")
    reviewed_at: Optional[datetime] = Field(default=None, description="审核时间")
    feedback: Optional[str] = Field(default=None, description="审核反馈")

    # 关系
    user: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[UserContribution.submitted_by]",
            "primaryjoin": "UserContribution.submitted_by == User.id"
        },
        back_populates="contributions"
    )
    reviewer: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[UserContribution.reviewed_by]",
            "primaryjoin": "UserContribution.reviewed_by == User.id"
        }
    )