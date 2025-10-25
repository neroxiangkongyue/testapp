import os
from typing import Optional
from pydantic import field_validator
from dotenv import load_dotenv

# 加载 .env 文件
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    应用配置类
    使用 pydantic 进行配置验证和类型转换
    """

    # ========== 应用基础配置 ==========
    APP_ENV: str = os.getenv("APP_ENV", "development")  # 当前运行环境（如 development/production/testing）
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"  # 是否启用调试模式
    APP_SECRET: str = os.getenv("APP_SECRET", "dev-secret")  # 应用主密钥

    # ========== 数据库配置 ==========
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")  # 数据库类型

    # SQLite 配置
    SQLITE_DATABASE_URL: str = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./word_graph1.db")  # SQLite 数据库文件路径

    # MySQL 配置
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "word_graph_user")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "word_graph")

    # 根据数据库类型生成数据库URL
    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_TYPE == "mysql":
            return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:" \
                   f"{self.MYSQL_PORT}/{self.MYSQL_DATABASE} "
        else:
            return self.SQLITE_DATABASE_URL

    # ========== JWT 配置 ==========
    # 用于管理用户身份验证和授权
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))

    # ========== Redis 配置 ==========
    # # 缓存用户信息（避免频繁查数据库）
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # ========== 第三方登录配置 ==========
    WECHAT_APPID: str = os.getenv("WECHAT_APPID", "")
    WECHAT_SECRET: str = os.getenv("WECHAT_SECRET", "")
    WECHAT_REDIRECT_URI: str = os.getenv("WECHAT_REDIRECT_URI", "")

    QQ_APPID: str = os.getenv("QQ_APPID", "")
    QQ_SECRET: str = os.getenv("QQ_SECRET", "")
    QQ_REDIRECT_URI: str = os.getenv("QQ_REDIRECT_URI", "")

    # ========== 邮件服务配置 ==========
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.qq.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "770782393@qq.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "cqvniouyrgtibeab")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "单词图学习系统")

    # ========== 短信服务配置 ==========
    SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "aliyun")
    SMS_ACCESS_KEY: str = os.getenv("SMS_ACCESS_KEY", "")
    SMS_ACCESS_SECRET: str = os.getenv("SMS_ACCESS_SECRET", "")
    SMS_SIGN_NAME: str = os.getenv("SMS_SIGN_NAME", "单词图")
    SMS_TEMPLATE_CODE: str = os.getenv("SMS_TEMPLATE_CODE", "SMS_123456789")

    # ========== 功能开关配置 ==========
    DISABLE_EMAIL_SENDING: bool = os.getenv("DISABLE_EMAIL_SENDING", "false").lower() == "true"
    DISABLE_SMS_SENDING: bool = os.getenv("DISABLE_SMS_SENDING", "false").lower() == "true"

    # ========== 验证配置 ==========
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v):
        if len(v) < 32 and os.getenv("APP_ENV") == "production":
            raise ValueError("生产环境JWT密钥长度必须至少32位")
        return v

    @field_validator("DATABASE_TYPE")
    @classmethod
    def validate_database_type(cls, v):
        if v not in ["sqlite", "mysql"]:
            raise ValueError("数据库类型必须是 sqlite 或 mysql")
        return v


# 创建全局配置实例
settings = Settings()

# 测试配置
if __name__ == "__main__":
    print(f"环境: {settings.APP_ENV}")
    print(f"数据库URL: {settings.DATABASE_URL}")
    print(f"Redis主机: {settings.REDIS_HOST}")
