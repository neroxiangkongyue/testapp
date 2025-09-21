# 关系相关的请求/响应模型
from pydantic import BaseModel
from typing import Optional, List


class RelationBase(BaseModel):
    source_id: int
    target_id: int
    relation_type_id: int
    weight: Optional[float] = 1.0
    description: str = ""


class RelationCreate(RelationBase):
    pass


class Relation(RelationBase):
    id: int

    class Config:
        from_attributes = True


class GraphPath(BaseModel):
    """表示两个单词之间的路径"""
    path: List[int]  # 单词ID的列表，表示路径
    relations: List[Optional[int]]  # 关系ID的列表，表示路径上的关系
    length: int  # 路径长度

    class Config:
        from_attributes = True