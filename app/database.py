from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel, Session
from contextlib import contextmanager
import os
from typing import Generator

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vocab5.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=True  # 开发时开启SQL日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 修复：使用 contextmanager 创建会话上下文
@contextmanager
def get_db_session():
    """提供数据库会话的上下文管理器（用于非FastAPI场景）"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# 修复：创建适合FastAPI的依赖项
def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖项，提供数据库会话"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_db_tables():
    """创建所有数据库表"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")


def drop_db_and_tables():
    """删除所有数据库表（仅用于开发和测试）"""
    print("Dropping database tables...")
    SQLModel.metadata.drop_all(engine)
    print("Database tables dropped successfully!")


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