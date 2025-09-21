# 认证服务
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.core.config import settings

def create_access_token(data: dict, expires_delta: timedelta = None):
    # 实现创建访问令牌逻辑
    pass

def verify_token(token: str):
    # 实现验证令牌逻辑
    pass