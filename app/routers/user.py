import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Dict

from app.auth.blacklist import add_to_blacklist
from app.crud.user import get_user_by_id
from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserPublicResponse
from app.auth.dependencies import get_current_user, security
from app.models.user import User

# 创建用户管理相关的路由组
users_router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)

@users_router.get("/me", response_model=UserResponse)
def get_current_user_info(
        current_user: User = Depends(get_current_user)  # 依赖注入当前用户
):
    """
    获取当前用户信息接口

    通过JWT令牌认证获取当前登录用户的详细信息
    这是一个需要认证的接口，必须提供有效的访问令牌

    Args:
        current_user: 通过依赖注入的当前用户对象

    Returns:
        UserResponse: 当前用户的详细信息
    """
    # 直接返回当前用户对象（依赖注入已经完成了用户查询和认证）
    return current_user


@users_router.get("/{user_id}", response_model=UserPublicResponse)
def get_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    根据用户ID获取用户信息接口

    公开接口，可以查看其他用户的基本信息（不包含敏感信息）

    Args:
        user_id: 要查询的用户ID
        db: 数据库会话

    Returns:
        UserResponse: 用户公开信息
    """
    # 根据ID查询用户
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 返回用户信息（自动过滤敏感字段，由UserResponse模型控制）
    return user


@users_router.put("/me", response_model=UserResponse)
def update_user_info(
        user_update: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    更新当前用户信息接口

    允许用户修改自己的基本信息，如显示名称、头像、手机号等
    只能修改允许的字段，不能修改用户名、邮箱等核心标识

    Args:
        user_update: 更新数据（只包含允许修改的字段）
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        UserResponse: 更新后的用户信息
    """
    # 从数据库重新获取用户对象（确保是最新数据）
    user = get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 将更新数据转换为字典，排除未设置的字段（exclude_unset=True）
    update_data = user_update.dict(exclude_unset=True)

    # 遍历更新字段，逐个设置到用户对象
    for field, value in update_data.items():
        setattr(user, field, value)

    # 保存更改到数据库
    db.add(user)
    db.commit()
    db.refresh(user)  # 刷新获取最新数据

    return user


@users_router.get("/{user_id}/profile", response_model=UserResponse)
def get_user_profile(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    获取用户公开资料接口

    用于查看其他用户的公开信息，如学习统计、成就等
    比基础用户信息接口返回更多公开数据

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        UserResponse: 用户公开资料
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 可以在这里添加更多的公开信息处理逻辑
    # 例如：学习统计、成就徽章、公开笔记等

    return user


@users_router.post("/me/logout", response_model=Dict[str, str])
def logout(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        current_user: User = Depends(get_current_user),
):
    """
    用户登出接口

    将当前使用的令牌加入黑名单，使其失效
    """
    try:
        token = credentials.credentials

        # 将令牌加入黑名单
        success = add_to_blacklist(token)

        if success:
            logger.info(f"用户 {current_user.display_name}(ID: {current_user.id}) 已登出")
            return {"message": "登出成功"}
        else:
            logger.warning(f"用户 {current_user.display_name} 登出失败，令牌可能已过期")
            return {"message": "登出失败，令牌可能已过期"}

    except Exception as e:
        logger.error(f"登出过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出过程发生错误"
        )


@users_router.post("/me/logout-all", response_model=Dict[str, str])
def logout_all(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    在所有设备上登出

    通过更新用户最后登出时间，使之前颁发的所有令牌失效
    """
    try:
        # 更新最后登出时间
        current_user.last_logout_at = datetime.utcnow()
        db.commit()

        logger.info(f"用户 {current_user.display_name} 已在所有设备上登出")
        return {"message": "已在所有设备上登出成功"}

    except Exception as e:
        db.rollback()
        logger.error(f"批量登出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量登出失败"
        )