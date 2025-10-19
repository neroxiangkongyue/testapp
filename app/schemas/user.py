from pydantic import BaseModel, EmailStr, validator, field_validator
from typing import Optional, List
from datetime import datetime
import re


class UserBase(BaseModel):
    display_name: str
    avatar: Optional[str] = None


class UserCreate(BaseModel):
    """用户创建基类"""
    login_type: str
    identifier: str
    display_name: str
    password: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    qq: Optional[str] = None
    wechat: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^[+]?[0-9]{10,15}$', v):
            raise ValueError('电话号码格式无效')
        return v



class EmailUserCreate(UserCreate):
    """邮箱用户创建"""
    login_type: str = "email"

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

    @field_validator('identifier')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('邮箱格式无效')
        return v.lower()


class PhoneUserCreate(UserCreate):
    """手机用户创建"""
    login_type: str = "phone"
    phone: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^[+]?[0-9]{10,15}$', v):
            raise ValueError('电话号码格式无效')
        return v


class WechatUserCreate(UserCreate):
    """微信用户创建"""
    login_type: str = "wechat"
    wechat_unionid: str
    display_name: str
    # 微信用户不需要密码


class QQUserCreate(UserCreate):
    """QQ用户创建"""
    login_type: str = "qq"
    qq_openid: str
    display_name: str
    # QQ用户不需要密码


class UserPublicResponse(BaseModel):
    id: int
    username: str
    display_name: str
    avatar: Optional[str]
    created_at: datetime

class UserResponse(BaseModel):
    id: int
    username: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    display_name: str
    avatar: Optional[str]
    auth_provider: str
    email_verified: bool
    phone_verified: bool
    is_premium: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


def validate_password_strength(password: str) -> str:
    """验证密码强度：至少8位，包含至少两种字符类型"""
    if len(password) < 8:
        raise ValueError('密码至少需要8个字符')

    # 检查字符类型
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    # 计算字符类型数量
    type_count = sum([has_letter, has_digit, has_special])

    if type_count < 2:
        raise ValueError('密码必须包含至少两种字符类型（字母、数字、符号）')

    return password


