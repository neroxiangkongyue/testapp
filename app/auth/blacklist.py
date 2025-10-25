import os
import random
import string
import uuid
import logging
import bcrypt
import redis
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status

# 从你的 config.py 导入设置
from app.config import settings

logger = logging.getLogger(__name__)

# ========== 常量定义 ==========
SECURE_JWT_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
DEFAULT_VERIFICATION_CODE_LENGTH = 6
DEFAULT_VERIFICATION_CODE_EXPIRE = 300  # 5分钟
MAX_VERIFICATION_ATTEMPTS = 3


# ========== Redis 客户端 ==========
def get_redis_client() -> Optional[redis.Redis]:
    """安全地创建Redis客户端，修复密码处理逻辑"""
    try:
        # 基础配置
        redis_kwargs: Dict[str, Any] = {
            'host': getattr(settings, 'REDIS_HOST', 'localhost'),
            'port': getattr(settings, 'REDIS_PORT', 6379),
            'db': getattr(settings, 'REDIS_DB', 0),
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_keepalive': True,
            'health_check_interval': 30,
        }

        # 只有在有密码且密码不为空字符串时才添加密码参数
        # redis_password = getattr(settings, 'REDIS_PASSWORD', None)
        # if redis_password and redis_password.strip():
        #     redis_kwargs['password'] = redis_password.strip()
        #     logger.info("使用密码连接Redis")
        # else:
        #     logger.info("无密码连接Redis")

        client = redis.Redis(**redis_kwargs)

        # 测试连接
        client.ping()
        logger.info("Redis客户端创建成功")
        return client

    except redis.AuthenticationError as e:
        logger.error(f"Redis认证失败: {e}")
        return None
    except redis.ConnectionError as e:
        logger.error(f"Redis连接失败: {e}")
        return None
    except Exception as e:
        logger.error(f"创建Redis客户端失败: {e}")
        return None


# Redis客户端单例
_redis_client = None


def get_redis_client_singleton() -> Optional[redis.Redis]:
    """获取Redis客户端单例"""
    global _redis_client
    if _redis_client is None:
        _redis_client = get_redis_client()
    return _redis_client


def is_redis_available() -> bool:
    """检查Redis是否可用"""
    client = get_redis_client_singleton()
    if not client:
        return False
    try:
        client.ping()
        return True
    except Exception:
        return False


# ========== 密码哈希工具 ==========
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"密码验证失败: {e}")
        return False


def get_password_hash(password: str) -> str:
    """生成密码的bcrypt哈希值"""
    try:
        # 添加密码强度检查
        if len(password) < 8:
            raise ValueError("密码长度至少8位")

        salt_rounds = getattr(settings, 'BCRYPT_ROUNDS', 12)
        hashed_bytes = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=salt_rounds)
        )
        return hashed_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"密码哈希失败: {e}")
        raise


# ========== JWT 令牌工具 ==========
def validate_jwt_config() -> None:
    """验证JWT配置安全性"""
    if not hasattr(settings, 'JWT_ALGORITHM'):
        raise ValueError("JWT算法未配置")

    if settings.JWT_ALGORITHM not in SECURE_JWT_ALGORITHMS:
        raise ValueError(f"不安全的JWT算法: {settings.JWT_ALGORITHM}")

    if settings.JWT_ALGORITHM == "none":
        raise ValueError("JWT 'none' 算法被明确禁止")

    # 检查密钥强度
    if settings.JWT_ALGORITHM.startswith('HS') and len(settings.JWT_SECRET_KEY) < 32:
        app_env = getattr(settings, 'APP_ENV', 'development')
        if app_env == "production":
            raise ValueError("生产环境HS算法JWT密钥长度必须至少32位")
        else:
            logger.warning("开发环境使用弱JWT密钥")


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access"
) -> str:
    """
    创建JWT访问令牌
    """
    validate_jwt_config()

    to_encode = data.copy()

    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == "refresh":
            expire_minutes = getattr(settings, 'JWT_REFRESH_TOKEN_EXPIRE_MINUTES', 10080)  # 7天
        else:
            expire_minutes = getattr(settings, 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30)
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)

    # 添加标准JWT声明
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "iss": getattr(settings, 'JWT_ISSUER', 'word-management-api'),
        "aud": getattr(settings, 'JWT_AUDIENCE', 'word-app-users'),
        "type": token_type,
    })

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    except Exception as e:
        logger.error(f"令牌创建失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌创建失败"
        )


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    验证并解码JWT令牌，同时检查是否在黑名单中
    """
    try:
        # 先检查是否在黑名单中
        if is_token_blacklisted(token):
            logger.warning("令牌已被加入黑名单")
            return None

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=getattr(settings, 'JWT_ISSUER', 'word-management-api'),
            audience=getattr(settings, 'JWT_AUDIENCE', 'word-app-users'),
            options={"verify_exp": True}
        )

        # 验证令牌类型
        if payload.get("type") != token_type:
            logger.warning(f"令牌类型不匹配: 期望{token_type}, 实际{payload.get('type')}")
            return None

        return payload

    except JWTError as e:
        logger.warning(f"JWT验证失败: {e}")
        return None
    except Exception as e:
        logger.error(f"令牌验证异常: {e}")
        return None


# ========== 令牌黑名单管理 ==========
def add_to_blacklist(token: str) -> bool:
    """
    将令牌加入黑名单
    """
    if not is_redis_available():
        logger.warning("Redis不可用，无法加入黑名单")
        return False

    redis_client = get_redis_client_singleton()

    try:
        payload = jwt.get_unverified_claims(token)
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            logger.warning("无效的令牌格式，缺少jti或exp")
            return False

        current_time = datetime.utcnow().timestamp()
        remaining_time = max(0, int(exp - current_time))

        if remaining_time > 0:
            key = f"blacklist:{jti}"
            # 使用setex设置过期时间，自动清理
            success = redis_client.setex(key, remaining_time, "revoked")
            if success:
                logger.info(f"令牌已加入黑名单，剩余时间: {remaining_time}秒")
            return bool(success)
        else:
            logger.info("令牌已过期，无需加入黑名单")
            return True  # 已过期的令牌视为成功

    except Exception as e:
        logger.error(f"加入黑名单失败: {e}")
        return False


def is_token_blacklisted(token: str) -> bool:
    """
    检查令牌是否在黑名单中
    """
    if not is_redis_available():
        return False

    redis_client = get_redis_client_singleton()

    try:
        payload = jwt.get_unverified_claims(token)
        jti = payload.get("jti")

        if not jti:
            return False

        key = f"blacklist:{jti}"
        return redis_client.exists(key) == 1

    except Exception as e:
        logger.error(f"检查黑名单失败: {e}")
        return False


def get_blacklist_count() -> int:
    """获取黑名单中的令牌数量"""
    if not is_redis_available():
        return 0

    redis_client = get_redis_client_singleton()
    try:
        # 注意：keys命令在生产环境可能阻塞，可以考虑使用SCAN
        keys = redis_client.keys("blacklist:*")
        return len(keys)
    except Exception as e:
        logger.error(f"获取黑名单数量失败: {e}")
        return 0


# ========== 验证码工具 ==========
def generate_verification_code(length: int = DEFAULT_VERIFICATION_CODE_LENGTH) -> str:
    """生成指定长度的数字验证码"""
    if length < 4:
        raise ValueError("验证码长度至少4位")
    return ''.join(random.choices(string.digits, k=length))


def store_verification_code(
        identifier: str,
        code: str,
        purpose: str,
        expires_in: int = DEFAULT_VERIFICATION_CODE_EXPIRE
) -> bool:
    """存储验证码到Redis"""
    if not is_redis_available():
        logger.warning("Redis不可用，无法存储验证码")
        return False

    redis_client = get_redis_client_singleton()

    if not all([identifier, code, purpose]):
        logger.error("验证码参数缺失")
        return False

    key = f"verify_code:{purpose}:{identifier}"
    try:
        # 使用事务确保原子操作
        pipeline = redis_client.pipeline()
        pipeline.setex(key, expires_in, code)
        # 同时设置尝试次数为0
        attempt_key = f"verify_attempts:{purpose}:{identifier}"
        pipeline.setex(attempt_key, expires_in, 0)
        pipeline.execute()

        logger.info(f"验证码存储成功: {key}")
        return True
    except Exception as e:
        logger.error(f"验证码存储失败: {e}")
        return False


def verify_code(
        identifier: str,
        code: str,
        purpose: str,
        max_attempts: int = MAX_VERIFICATION_ATTEMPTS
) -> bool:
    """验证验证码是否正确"""
    if not is_redis_available():
        logger.warning("Redis不可用，无法验证验证码")
        return False

    redis_client = get_redis_client_singleton()

    if not all([identifier, code, purpose]):
        return False

    attempt_key = f"verify_attempts:{purpose}:{identifier}"
    code_key = f"verify_code:{purpose}:{identifier}"

    try:
        # 使用事务确保原子性
        pipeline = redis_client.pipeline()
        pipeline.get(attempt_key)
        pipeline.get(code_key)
        attempts, stored_code = pipeline.execute()

        # 检查尝试次数
        current_attempts = int(attempts or 0)
        if current_attempts >= max_attempts:
            logger.warning(f"验证码尝试次数超限: {identifier}")
            return False

        # 获取并比对验证码
        if stored_code and stored_code.strip() == code.strip():
            # 验证成功，删除相关key
            pipeline = redis_client.pipeline()
            pipeline.delete(code_key, attempt_key)
            pipeline.execute()
            logger.info("验证码验证成功")
            return True
        else:
            # 验证失败，增加尝试次数
            pipeline = redis_client.pipeline()
            pipeline.incr(attempt_key)
            pipeline.expire(attempt_key, 3600)  # 尝试次数记录保留1小时
            pipeline.execute()
            logger.warning("验证码不匹配")
            return False

    except Exception as e:
        logger.error(f"验证码验证异常: {e}")
        return False


# ========== 用户名生成工具 ==========
def generate_username(prefix: str = "user") -> str:
    """为第三方登录用户生成唯一用户名"""
    random_suffix = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}_{random_suffix}"


# ========== 健康检查 ==========
def health_check() -> Dict[str, Any]:
    """安全模块健康检查"""
    redis_available = is_redis_available()

    status_info = {
        "redis": "connected" if redis_available else "disconnected",
        "jwt_config": "valid",
        "blacklist_count": get_blacklist_count() if redis_available else 0,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        validate_jwt_config()
    except Exception as e:
        status_info["jwt_config"] = f"invalid: {str(e)}"

    return status_info


# ========== 测试函数 ==========
def test_security_functions() -> None:
    """测试安全相关功能"""
    print("开始测试安全功能...")

    # 检查Redis状态
    if is_redis_available():
        print("✅ Redis连接正常")
    else:
        print("⚠️ Redis不可用，跳过Redis相关测试")

    try:
        # 测试密码哈希
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed), "密码验证失败"
        print("✅ 密码功能测试通过")

        # 测试JWT令牌
        token_data = {"user_id": 1, "username": "test_user"}
        token = create_access_token(token_data)
        decoded = verify_token(token)
        assert decoded is not None, "JWT验证失败"
        assert decoded["user_id"] == 1, "JWT数据解码错误"
        print("✅ JWT功能测试通过")

        if is_redis_available():
            # 测试验证码
            test_code = generate_verification_code()
            success = store_verification_code("test@example.com", test_code, "register")
            if success:
                assert verify_code("test@example.com", test_code, "register"), "验证码验证失败"
                print("✅ 验证码功能测试通过")
            else:
                print("⚠️ 验证码存储失败，跳过验证码测试")

            # 测试黑名单功能
            if add_to_blacklist(token):
                assert is_token_blacklisted(token), "黑名单检查失败"
                assert verify_token(token) is None, "黑名单令牌应该验证失败"
                print("✅ 黑名单功能测试通过")
            else:
                print("⚠️ 加入黑名单失败，跳过黑名单测试")
        else:
            print("⚠️ Redis不可用，跳过验证码和黑名单测试")

        print("🎉 安全功能测试完成")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_security_functions()