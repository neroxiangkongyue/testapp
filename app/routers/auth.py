
from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict
# 导入服务类
from app.services.email_service import email_service
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.schemas.auth import *
from app.schemas.user import *
from app.crud.user import *
from app.crud.auth import *
from app.auth.blacklist import *
from app.services.third_party_auth import WechatAuthService, QQAuthService

auths_router = APIRouter(prefix="/auth", tags=["authentication"])

# 配置日志
logger = logging.getLogger(__name__)


async def send_verification_message(identifier: str, code: str, purpose: str):
    """发送验证消息"""
    try:
        if "@" in identifier:
            success = email_service.send_verification_email(identifier, code, purpose)
            if success:
                logger.info(f"验证码邮件发送成功: {identifier}")
            else:
                logger.error(f"验证码邮件发送失败: {identifier}")
        else:
            # 短信发送逻辑（这里简单模拟）
            logger.info(f"模拟发送短信到 {identifier}: 验证码 {code}")

    except Exception as e:
        logger.error(f"发送验证消息异常: {identifier}, 错误: {str(e)}")


@auths_router.post("/send-verification-code")
async def send_verification_code(request: SendCodeRequest, background_tasks: BackgroundTasks):
    """
    发送验证码接口

    支持向邮箱或手机号发送验证码，用于注册、登录或重置密码等场景
    使用BackgroundTasks异步发送，避免阻塞API响应

    Args:
        request: 发送验证码请求，包含标识符和用途
        background_tasks: FastAPI后台任务，用于异步发送消息

    Returns:
        Dict: 包含操作结果的字典
    """
    # 验证邮箱或手机号格式
    if "@" in request.identifier:
        # 邮箱验证
        if not re.match(r'^[a-zA-Z\d._%+-]+@[a-zA-Z\d.-]+\.[a-zA-Z]{2,}$', request.identifier):
            raise HTTPException(status_code=400, detail="邮箱格式无效")
    else:
        # 手机号验证
        if not re.match(r'^[+]?\d{10,15}$', request.identifier):
            raise HTTPException(status_code=400, detail="手机号格式无效")

    # 生成验证码
    code = generate_verification_code()
    # print(request.identifier, request.purpose, code)
    # 存储验证码
    if not store_verification_code(request.identifier, code, request.purpose):
        raise HTTPException(status_code=500, detail="验证码发送失败")
    # print("store_verification_code:", store_verification_code(request.identifier, code, request.purpose))
    # 后台发送邮件或短信
    background_tasks.add_task(send_verification_message, request.identifier, code, request.purpose)
    print("发送验证码到{}成功".format(request.identifier))
    return {"message": "验证码已发送"}


@auths_router.post("/register")
def register(register_request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口

    支持多种注册方式：邮箱、手机号、微信、QQ
    根据不同的登录类型采用不同的注册逻辑

    Args:
        register_request: 注册请求数据: 注册方式、标识符、密码、展示名、验证码
        db: 数据库会话依赖注入

    Returns:
        Token: 注册成功后的访问令牌和用户信息
    """
    # 验证验证码（邮箱/手机注册时需要）
    if register_request.login_type in [LoginType.EMAIL, LoginType.PHONE]:
        if not register_request.verification_code:
            raise HTTPException(status_code=400, detail="需要验证码")

        if not verify_code(register_request.identifier, register_request.verification_code, "register"):
            raise HTTPException(status_code=400, detail="验证码错误或已过期")

    # 检查标识符是否已存在
    existing_user = get_user_by_identifier(db, register_request.identifier)
    if existing_user:
        raise HTTPException(status_code=400, detail="该账号已被注册")

    # 根据登录类型创建用户
    if register_request.login_type == LoginType.EMAIL:
        if not register_request.password:
            raise HTTPException(status_code=400, detail="邮箱注册需要密码")

        user_create = EmailUserCreate(
            identifier=register_request.identifier,
            password=register_request.password,
            display_name=register_request.display_name
        )
        user = create_email_user(db, user_create)

    elif register_request.login_type == LoginType.PHONE:
        if not register_request.password:
            raise HTTPException(status_code=400, detail="手机注册需要密码")

        user_create = PhoneUserCreate(
            phone=register_request.identifier,
            password=register_request.password,
            display_name=register_request.display_name
        )
        user = create_phone_user(db, user_create)

    elif register_request.login_type == LoginType.WECHAT:
        # 1. 用code换access_token和openid
        token_data = WechatAuthService.get_access_token(register_request.verification_code)
        if not token_data:
            raise HTTPException(status_code=400, detail="微信授权码无效")

        # 2. 获取用户信息
        user_info = WechatAuthService.get_user_info(
            token_data['access_token'],
            token_data['openid']
        )
        if not user_info:
            raise HTTPException(status_code=400, detail="微信用户信息获取失败")

        # 3. 创建用户
        user_create = WechatUserCreate(
            wechat_unionid=user_info['unionid'],
            display_name=register_request.display_name or user_info.get('nickname', '微信用户')
        )
        user = create_wechat_user(db, user_create)

    elif register_request.login_type == LoginType.QQ:
        # QQ注册需要先获取用户信息
        qq_data = QQAuthService.get_openid(register_request.identifier)
        if not qq_data:
            raise HTTPException(status_code=400, detail="QQ授权失败")

        user_create = QQUserCreate(
            qq_openid=qq_data['openid'],
            display_name=register_request.display_name or 'QQ用户'
        )
        user = create_qq_user(db, user_create)

    else:
        raise HTTPException(status_code=400, detail="不支持的登录方式")

    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.display_name, "user_id": user.id}
    )

    print("注册用户{}成功".format(user.display_name))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.display_name,
        "has_password": user.hashed_password is not None,
        "auth_provider": user.auth_provider.value
    }


@auths_router.post("/login")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """
        用户登录接口

        支持多种登录方式，根据登录类型采用不同的认证逻辑
        登录成功后更新最后登录时间并返回访问令牌

        Args:
            login_request: 登录请求数据
            db: 数据库会话

        Returns:
            Token: 登录成功后的访问令牌
    """
    user = None

    if login_request.login_type == LoginType.EMAIL:
        if not login_request.password:
            raise HTTPException(status_code=400, detail="邮箱登录需要密码")

        user = authenticate_email_user(db, login_request.identifier, login_request.password)

    elif login_request.login_type == LoginType.PHONE:
        if not login_request.password:
            raise HTTPException(status_code=400, detail="手机登录需要密码")

        user = authenticate_phone_user(db, login_request.identifier, login_request.password)

    elif login_request.login_type == LoginType.WECHAT:
        # 微信登录通过授权码获取unionid
        wechat_data = WechatAuthService.get_access_token(login_request.auth_code)
        if wechat_data:
            user_info = WechatAuthService.get_user_info(
                wechat_data['access_token'], wechat_data['openid']
            )
            if user_info:
                user = authenticate_wechat_user(db, user_info['unionid'])

    elif login_request.login_type == LoginType.QQ:
        # QQ登录通过授权码获取openid
        redirect_uri = os.getenv("QQ_REDIRECT_URI", "")
        qq_data = QQAuthService.get_access_token(login_request.auth_code, redirect_uri)
        if qq_data:
            openid_data = QQAuthService.get_openid(qq_data['access_token'])
            if openid_data:
                user = authenticate_qq_user(db, openid_data['openid'])
    else:
        raise HTTPException(status_code=400, detail="登录类型错误")
    if not user:
        raise HTTPException(status_code=400, detail="登录失败，请检查账号和密码")

    # 更新最后登录时间
    update_user_last_login(db, user.id)

    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.display_name, "user_id": user.id}
    )
    print("登录用户{}成功".format(user.display_name))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.display_name,
        "has_password": user.hashed_password is not None,
        "auth_provider": user.auth_provider.value
    }


@auths_router.post("/bind-third-party")
def bind_third_party(
        bind_request: BindThirdPartyRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    绑定第三方账号接口

    将微信或QQ账号绑定到当前登录的用户账号
    绑定后可以使用第三方账号快速登录

    Args:
        bind_request: 绑定请求数据
        db: 数据库会话
        current_user: 当前登录用户（通过JWT令牌认证）

    Returns:
        Dict: 绑定结果
    """
    # 获取第三方用户信息
    if bind_request.provider == "wechat":
        wechat_data = WechatAuthService.get_access_token(bind_request.auth_code)
        if not wechat_data:
            raise HTTPException(status_code=400, detail="微信授权失败")

        user_info = WechatAuthService.get_user_info(
            wechat_data['access_token'], wechat_data['openid']
        )
        if not user_info:
            raise HTTPException(status_code=400, detail="获取微信用户信息失败")

        unionid = user_info['unionid']

        # 检查是否已被其他账号绑定
        existing_user = get_user_by_wechat(db, unionid)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="该微信账号已被绑定")

        # 绑定到当前用户
        success = bind_third_party_to_user(db, current_user.id, "wechat", unionid)

    elif bind_request.provider == "qq":
        redirect_uri = os.getenv("QQ_REDIRECT_URI", "")
        qq_data = QQAuthService.get_access_token(bind_request.auth_code, redirect_uri)
        if not qq_data:
            raise HTTPException(status_code=400, detail="QQ授权失败")

        openid_data = QQAuthService.get_openid(qq_data['access_token'])
        if not openid_data:
            raise HTTPException(status_code=400, detail="获取QQ OpenID失败")

        openid = openid_data['openid']

        # 检查是否已被其他账号绑定
        existing_user = get_user_by_qq(db, openid)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="该QQ账号已被绑定")

        # 绑定到当前用户
        success = bind_third_party_to_user(db, current_user.id, "qq", openid)

    else:
        raise HTTPException(status_code=400, detail="不支持的第三方平台")

    if not success:
        raise HTTPException(status_code=500, detail="绑定失败")

    return {"message": "绑定成功"}


@auths_router.post("/verify-token", response_model=Dict[str, Any])
def verify_access_token(token: str):
    """
    验证访问令牌接口

    用于前端检查令牌是否有效，或者获取令牌中的用户信息

    Args:
        token: JWT访问令牌

    Returns:
        Dict: 令牌验证结果和用户信息
    """
    # 解码并验证令牌
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期"
        )

    # 返回令牌中的用户信息
    return {
        "valid": True,
        "username": payload.get("sub"),
        "user_id": payload.get("user_id")
    }


@auths_router.post("/reset-password", response_model=Dict[str, str])
def reset_password(
        reset_request: ResetPasswordRequest,
        db: Session = Depends(get_db)
):
    """
    重置密码接口

    通过验证码验证身份后重置用户密码
    支持邮箱和手机号两种方式的密码重置

    Args:
        reset_request: 重置密码请求
        db: 数据库会话

    Returns:
        Dict: 重置结果
    """
    # 验证验证码
    if not verify_code(reset_request.identifier, reset_request.code, "reset_password"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    # 查找用户
    user = get_user_by_identifier(db, reset_request.identifier)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 验证新密码强度
    try:
        validated_password = validate_password_strength(reset_request.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 更新密码
    user.hashed_password = get_password_hash(validated_password)
    db.add(user)
    db.commit()

    return {"message": "密码重置成功"}


