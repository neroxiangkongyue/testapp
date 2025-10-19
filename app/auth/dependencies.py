from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Optional

from app.database import get_db
from app.crud.user import get_user_by_id
from app.auth.blacklist import verify_token, is_token_blacklisted
from app.models.user import User

# 创建HTTP Bearer认证方案
# 客户端需要在Authorization头中携带: Bearer <token>
security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),  # 提取Authorization头
        db: Session = Depends(get_db)  # 数据库会话依赖
) -> User:
    """
    获取当前登录用户的依赖函数

    这个函数会被用作FastAPI的依赖注入，用于需要认证的接口
    它会自动验证JWT令牌并返回对应的用户对象

    Args:
        credentials: 包含Bearer令牌的认证凭证
        db: 数据库会话

    Returns:
        User: 认证成功的用户对象

    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    # 定义认证失败的统一异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},  # 告诉客户端使用Bearer认证
    )

    # 从Bearer令牌中提取token
    token = credentials.credentials
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已失效，请重新登录",
        )

    # 验证令牌有效性
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception  # 令牌无效

    # 从令牌载荷中提取用户信息
    username: str = payload.get("sub")  # 主题（通常是用户名）
    user_id: int = payload.get("user_id")  # 用户ID

    # 检查必需字段是否存在
    if username is None or user_id is None:
        raise credentials_exception  # 令牌格式错误

    # 根据用户ID从数据库查询用户
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception  # 用户不存在

    # 检查用户状态是否正常
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 返回认证成功的用户对象
    return user


async def get_optional_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> Optional[User]:
    """
    可选的当前用户依赖函数

    用于那些既支持认证访问又支持匿名访问的接口
    如果提供了有效令牌则返回用户，否则返回None

    Args:
        credentials: 可选的认证凭证
        db: 数据库会话

    Returns:
        Optional[User]: 用户对象或None
    """
    if credentials is None:
        return None  # 没有提供认证信息，返回匿名访问

    try:
        # 尝试获取当前用户
        return await get_current_user(credentials, db)
    except HTTPException:
        return None  # 认证失败，返回匿名访问