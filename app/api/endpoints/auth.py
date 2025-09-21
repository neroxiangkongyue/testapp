# 认证相关端点
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.schemas.user import UserCreate, User, Token
from app.crud.user import create_user, get_user_by_username
from app.core.security import get_password_hash, verify_password

router = APIRouter()

@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 实现用户注册逻辑
    pass

@router.post("/login", response_model=Token)
def login():
    # 实现用户登录逻辑
    pass