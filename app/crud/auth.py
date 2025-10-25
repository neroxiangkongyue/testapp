from typing import Optional

from sqlmodel import Session

from app.crud.user import get_user_by_email, get_user_by_phone, get_user_by_wechat, get_user_by_qq
from app.models.user import User
from app.auth.security import verify_password


def authenticate_email_user(db: Session, email: str, password: str) -> Optional[User]:
    """验证邮箱用户"""
    user = get_user_by_email(db, email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def authenticate_phone_user(db: Session, phone: str, password: str) -> Optional[User]:
    """验证手机用户"""
    user = get_user_by_phone(db, phone)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def authenticate_wechat_user(db: Session, unionid: str) -> Optional[User]:
    """验证微信用户"""
    return get_user_by_wechat(db, unionid)


def authenticate_qq_user(db: Session, openid: str) -> Optional[User]:
    """验证QQ用户"""
    return get_user_by_qq(db, openid)
