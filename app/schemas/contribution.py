# 贡献相关的请求/响应模型
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.contribution import ContributionType, ContributionStatus

class ContributionBase(BaseModel):
    type: ContributionType
    data: str

class ContributionCreate(ContributionBase):
    pass

class Contribution(ContributionBase):
    id: int
    status: ContributionStatus
    submitted_by: int
    submitted_at: datetime
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    feedback: Optional[str]
    
    class Config:
        from_attributes = True