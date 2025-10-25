from app.config import settings

# 访问配置
print(f"当前环境: {settings.APP_ENV}")
print(f"数据库URL: {settings.DATABASE_URL}")
print(f"JWT密钥长度: {len(settings.JWT_SECRET_KEY)}")

# 根据环境执行不同的逻辑
if settings.APP_ENV == "development":
    # 开发环境特定逻辑
    print("这是开发环境")
elif settings.APP_ENV == "production":
    # 生产环境特定逻辑
    print("这是生产环境")