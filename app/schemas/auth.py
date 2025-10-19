from pydantic import BaseModel
from typing import Optional, Literal
from app.schemas.enums import LoginType


class RegisterRequest(BaseModel):
    """用户注册请求数据模型"""
    login_type: LoginType  # 注册使用的登录方式
    identifier: str  # 标识符：邮箱、手机号、微信授权码、QQ授权码
    password: Optional[str] = None  # 密码：邮箱/手机注册时需要，第三方登录不需要
    display_name: str  # 用户显示名称
    verification_code: Optional[str] = None  # 验证码：邮箱/手机注册时需要


class LoginRequest(BaseModel):
    """用户登录请求数据模型"""
    login_type: LoginType  # 登录方式
    identifier: str  # 标识符
    password: Optional[str] = None  # 密码：邮箱/手机登录时需要
    auth_code: Optional[str] = None  # 授权码：第三方登录时需要


class BindThirdPartyRequest(BaseModel):
    """绑定第三方账号请求数据模型"""
    provider: Literal["wechat", "qq"]  # 第三方平台类型
    auth_code: str  # 第三方授权码
    bind_to_email: Optional[str] = None  # 绑定到已有邮箱账号
    bind_to_phone: Optional[str] = None  # 绑定到已有手机账号


class VerifyCodeRequest(BaseModel):
    """验证码验证请求数据模型"""
    identifier: str  # 邮箱或手机号
    code: str  # 验证码
    purpose: Literal["register", "login", "reset_password"]  # 验证码用途


class SendCodeRequest(BaseModel):
    """发送验证码请求数据模型"""
    identifier: str  # 邮箱或手机号
    purpose: Literal["register", "login", "reset_password"]  # 验证码用途


class ResetPasswordRequest(BaseModel):
    """重置密码请求数据模型"""
    identifier: str  # 邮箱或手机号
    code: str  # 验证码
    new_password: str  # 新密码


class Token(BaseModel):
    """登录令牌响应数据模型"""
    access_token: str  # JWT访问令牌
    token_type: str  # 令牌类型，通常是"bearer"
    user_id: int  # 用户ID
    username: str  # 用户名（显示名称）
    has_password: bool  # 是否设置了密码（用于提示用户设置密码）
    auth_provider: str  # 当前使用的认证方式
