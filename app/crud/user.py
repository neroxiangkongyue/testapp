from sqlalchemy import or_
from sqlmodel import Session, select
from typing import Optional, List
from app.models.user import User, AuthProvider
from app.schemas.user import EmailUserCreate, PhoneUserCreate, WechatUserCreate, QQUserCreate, UserUpdate
from app.auth.security import get_password_hash, generate_username

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def create_email_user(db: Session, user_create: EmailUserCreate) -> User:
    """创建邮箱用户"""
    username = generate_username()
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.identifier,
        username=username,
        display_name=user_create.display_name,
        hashed_password=hashed_password,
        auth_provider=AuthProvider.EMAIL,
        email_verified=False  # 需要验证后设为True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_phone_user(db: Session, user_create: PhoneUserCreate) -> User:
    """创建手机用户"""
    hashed_password = get_password_hash(user_create.password)

    db_user = User(
        phone=user_create.phone,
        display_name=user_create.display_name,
        hashed_password=hashed_password,
        auth_provider=AuthProvider.PHONE,
        phone_verified=False  # 需要验证后设为True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_wechat_user(db: Session, user_create: WechatUserCreate) -> User:
    """创建微信用户"""
    # 为微信用户生成唯一用户名
    username = generate_username()

    db_user = User(
        username=username,
        wechat_unionid=user_create.wechat_unionid,
        display_name=user_create.display_name,
        auth_provider=AuthProvider.WECHAT
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_qq_user(db: Session, user_create: QQUserCreate) -> User:
    """创建QQ用户"""
    # 为QQ用户生成唯一用户名
    username = generate_username()

    db_user = User(
        username=username,
        qq_openid=user_create.qq_openid,
        display_name=user_create.display_name,
        auth_provider=AuthProvider.QQ
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """根据任意标识符获取用户（邮箱、手机、微信、QQ）"""
    statement = select(User).where(
        (User.email == identifier) |
        (User.phone == identifier) |
        (User.wechat_unionid == identifier) |
        (User.qq_openid == identifier)
    )
    return db.scalars(statement).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据用户名获取用户"""
    statement = select(User).where(User.id == user_id)
    return db.execute(statement).scalars().first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    statement = select(User).where(User.username == username)
    return db.execute(statement).scalars().first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return db.execute(statement).scalars().first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    statement = select(User).where(User.phone == phone)
    return db.execute(statement).scalars().first()


def get_user_by_wechat(db: Session, unionid: str) -> Optional[User]:
    statement = select(User).where(User.wechat_unionid == unionid)
    return db.execute(statement).scalars().first()


def get_user_by_qq(db: Session, openid: str) -> Optional[User]:
    statement = select(User).where(User.qq_openid == openid)
    return db.execute(statement).scalars().first()


def bind_third_party_to_user(db: Session, user_id: int, provider: str, unionid: str) -> bool:
    """绑定第三方账号到现有用户"""
    user = db.get(User, user_id)
    if not user:
        return False

    if provider == "wechat":
        user.wechat_unionid = unionid
    elif provider == "qq":
        user.qq_openid = unionid
    else:
        return False

    db.add(user)
    db.commit()
    db.refresh(user)
    return True


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    更新用户信息

    Args:
        db: 数据库会话
        user_id: 用户ID
        user_update: 更新数据

    Returns:
        Optional[User]: 更新后的用户对象
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    # 将更新数据转换为字典，排除未设置的字段
    update_data = user_update.dict(exclude_unset=True)

    # 遍历更新字段
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: int, new_password: str) -> bool:
    """
    更新用户密码

    Args:
        db: 数据库会话
        user_id: 用户ID
        new_password: 新密码

    Returns:
        bool: 更新是否成功
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    return True


def update_user_last_login(db: Session, user_id: int):
    """更新用户最后登录时间为当前时间"""
    user = db.get(User, user_id)
    if user:
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)


def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户（软删除，实际是标记为停用）

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        bool: 删除是否成功
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    user.status = "inactive"  # 标记为未激活状态（软删除）
    db.add(user)
    db.commit()
    return True


def get_users(db: Session, user_ids: List[int]) -> List[User]:
    """
    根据ID列表查询多个用户
    :param db: 数据库会话
    :param user_ids: 用户ID列表
    :return: 用户对象列表
    """
    if not user_ids:
        return []

    stmt = select(User).where(User.id.in_(user_ids))  # type: ignore
    return db.scalars(stmt).all()


def search_users(db: Session, keyword: str, limit: int = 10) -> List[User]:
    """
    更健壮的搜索实现：
    - 自动处理空关键词
    - 防止SQL注入
    - 优化模糊匹配
    """
    if not keyword.strip():
        return []

    stmt = (
        select(User)
        .where(
            or_(
                User.username.ilike(f"%{keyword}%"),
                User.display_name.ilike(f"%{keyword}%")
            )
        )
        .limit(limit)
    )

    return db.scalars(stmt).all()