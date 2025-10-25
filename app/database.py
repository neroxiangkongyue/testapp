from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel, Session
from contextlib import contextmanager
from typing import Generator

# 导入配置类
from app.config import settings



def get_database_engine():
    """
    根据配置创建数据库引擎

    根据不同的环境使用不同的数据库配置
    """
    database_url = settings.DATABASE_URL

    if settings.DATABASE_TYPE == "sqlite":
        # SQLite 配置
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG  # 开发环境显示SQL日志
        )
    else:
        # MySQL 配置
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # 连接前ping检测
            pool_recycle=300,  # 连接回收时间
            echo=settings.DEBUG  # 开发环境显示SQL日志
        )

    return engine


# 创建数据库引擎
engine = get_database_engine()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session():
    """
    数据库会话上下文管理器（用于非FastAPI场景）

    使用示例：
    with get_db_session() as session:
        # 使用session进行数据库操作
        user = session.get(User, 1)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()  # 成功时提交事务
    except Exception as e:
        session.rollback()  # 异常时回滚事务
        raise e
    finally:
        session.close()  # 确保会话关闭


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 依赖项，提供数据库会话

    在FastAPI路由中使用：
    @app.get("/users/{user_id}")
    def get_user(user_id: int, db: Session = Depends(get_db)):
        user = db.get(User, user_id)
        return user
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # 请求成功完成时提交
    except Exception:
        db.rollback()  # 发生异常时回滚
        raise
    finally:
        db.close()  # 请求结束时关闭连接


def create_db_tables():
    """创建所有数据库表"""
    print(f"创建数据库表，环境: {settings.APP_ENV}")
    SQLModel.metadata.create_all(engine)
    print("数据库表创建成功!")


def drop_db_tables():
    """删除所有数据库表（仅用于开发和测试）"""
    if settings.APP_ENV == "production":
        raise Exception("生产环境禁止删除数据库表!")

    print("删除数据库表...")
    SQLModel.metadata.drop_all(engine)
    print("数据库表删除成功!")


def init_db():
    """初始化数据库（创建表并添加初始数据）"""
    # 注意：这里使用相对导入，确保在包内运行
    try:
        from .init_data import import_initial_data
    except ImportError:
        # 如果直接运行此脚本，使用绝对导入
        from init_data import import_initial_data

    # 创建数据库表
    create_db_tables()

    # 导入初始数据
    import_initial_data()
    print("Database initialized with sample data!")


# 开发时自动初始化数据库
if __name__ == "__main__":
    init_db()