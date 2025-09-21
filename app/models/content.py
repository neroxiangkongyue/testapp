from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class DifficultyLevel(SQLModel, table=True):
    __tablename__ = "difficultylevel"
    """难度级别表，定义单词的难度等级"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, description="难度级别名称")
    description: Optional[str] = Field(default=None, description="难度级别描述")
    min_frequency: Optional[int] = Field(default=None, description="最小词频")
    max_frequency: Optional[int] = Field(default=None, description="最大词频")
    color_code: Optional[str] = Field(default=None, description="颜色代码（用于UI显示）")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    # 关系
    words: List["Word"] = Relationship(back_populates="difficulty_level")


class Category(SQLModel, table=True):
    """分类表，用于对单词进行分类"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="分类名称")
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id", description="父分类ID")

    # 关系
    words: List["WordCategory"] = Relationship(back_populates="category")


class Tag(SQLModel, table=True):
    """标签表，用于标记单词的特性"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="标签名称")

    # 关系
    words: List["WordTag"] = Relationship(back_populates="tag")