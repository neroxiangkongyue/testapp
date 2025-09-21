# 用户CRUD操作
from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user(db: Session, user_id: int):
    return db.exec(select(User).where(User.id == user_id)).first()

def get_user_by_username(db: Session, username: str):
    return db.exec(select(User).where(User.username == username)).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.exec(select(User).offset(skip).limit(limit)).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user