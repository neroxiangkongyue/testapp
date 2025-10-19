from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.user import get_user_by_id
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.book import (
    RelationBookCreate, RelationBookUpdate, RelationBook, RelationBookBrief, RelationBookWithRelations,
    RelationBookRelationLinkCreate, WordRelationBrief, UserBrief
)
from app.crud.book import (
    create_relation_book, get_relation_book, get_relation_book_with_visibility_check, get_relation_books,
    get_user_relation_books, get_collected_relation_books, update_relation_book, delete_relation_book,
    add_relation_to_relation_book, remove_relation_from_relation_book, get_relation_book_relations,
    collect_relation_book, uncollect_relation_book, check_relation_book_collected
)
from app.crud.relation import get_relation

relation_books_router = APIRouter(prefix="/relation-books", tags=["relation books"])


@relation_books_router.post("/", response_model=RelationBook, status_code=status.HTTP_201_CREATED)
def create_new_relation_book(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    relation_book_in: RelationBookCreate
):
    """创建新关系库"""
    relation_book = create_relation_book(db, relation_book_in, current_user.id)
    return relation_book


@relation_books_router.get("/", response_model=List[RelationBookBrief])
def read_relation_books(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_public: Optional[bool] = None,
    keyword: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取关系库列表（考虑可见性）"""
    user_id = current_user.id if current_user else None
    relation_books = get_relation_books(db, skip=skip, limit=limit, user_id=user_id, is_public=is_public, keyword=keyword)
    return relation_books


@relation_books_router.get("/my-relation-books", response_model=List[RelationBookBrief])
def read_my_relation_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """获取当前用户创建的关系库"""
    relation_books = get_user_relation_books(db, current_user.id, skip=skip, limit=limit)
    return relation_books


@relation_books_router.get("/collected", response_model=List[RelationBookBrief])
def read_collected_relation_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """获取当前用户收藏的关系库"""
    relation_books = get_collected_relation_books(db, current_user.id, skip=skip, limit=limit)
    return relation_books


@relation_books_router.get("/{relation_book_id}", response_model=RelationBookWithRelations)
def read_relation_book(
    *,
    db: Session = Depends(get_db),
    relation_book_id: int,
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取关系库详情（考虑可见性）"""
    user_id = current_user.id if current_user else None
    relation_book = get_relation_book_with_visibility_check(db, relation_book_id, user_id)

    if not relation_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation book not found or access denied"
        )

    # 获取关联的关系
    relation_ids = get_relation_book_relations(db, relation_book_id)
    relations = []
    for relation_id in relation_ids:
        relation = get_relation(db, relation_id)
        if relation:
            relations.append(WordRelationBrief.from_orm(relation))

    # 获取创建者信息
    creator = get_user_by_id(db, relation_book.creator_id)

    # 检查当前用户是否收藏
    is_collected = False
    if current_user:
        is_collected = check_relation_book_collected(db, relation_book_id, current_user.id)

    # 构建响应
    relation_book_response = RelationBookWithRelations(
        **relation_book.dict(),
        relations=relations,
        creator=UserBrief.from_orm(creator) if creator else None,
        is_collected=is_collected
    )

    return relation_book_response


@relation_books_router.put("/{relation_book_id}", response_model=RelationBook)
def update_relation_book_details(
    *,
    db: Session = Depends(get_db),
    relation_book_id: int,
    relation_book_in: RelationBookUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新关系库"""
    relation_book = get_relation_book(db, relation_book_id)
    if not relation_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation book not found"
        )

    if relation_book.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this relation book"
        )

    relation_book = update_relation_book(db, relation_book, relation_book_in)
    return relation_book


@relation_books_router.delete("/{relation_book_id}")
def delete_relation_book_by_id(
    *,
    db: Session = Depends(get_db),
    relation_book_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除关系库"""
    relation_book = get_relation_book(db, relation_book_id)
    if not relation_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation book not found"
        )

    if relation_book.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this relation book"
        )

    success = delete_relation_book(db, relation_book)
    if success:
        return {"message": "Relation book deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed"
        )


@relation_books_router.post("/{relation_book_id}/relations")
def add_relation_to_relation_book_route(
    *,
    db: Session = Depends(get_db),
    relation_book_id: int,
    relation_link_in: RelationBookRelationLinkCreate,
    current_user: User = Depends(get_current_user)
):
    """添加关系到关系库"""
    relation_book = get_relation_book(db, relation_book_id)
    if not relation_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation book not found"
        )

    if relation_book.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this relation book"
        )

    success = add_relation_to_relation_book(db, relation_book_id, relation_link_in.relation_id, relation_link_in.order, relation_link_in.note)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add relation to relation book (relation not found or already exists)"
        )

    return {"message": "Relation added to relation book successfully"}


@relation_books_router.delete("/{relation_book_id}/relations/{relation_id}")
def remove_relation_from_relation_book_route(
    *,
    db: Session = Depends(get_db),
    relation_book_id: int,
    relation_id: int,
    current_user: User = Depends(get_current_user)
):
    """从关系库移除关系"""
    relation_book = get_relation_book(db, relation_book_id)
    if not relation_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation book not found"
        )

    if relation_book.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this relation book"
        )

    success = remove_relation_from_relation_book(db, relation_book_id, relation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relation not found in relation book"
        )

    return {"message": "Relation removed from relation book successfully"}


@relation_books_router.post("/{relation_book_id}/collect")
def collect_relation_book_by_id(
    *,
    db: Session = Depends(get_db),
    relation_book_id: int,
    current_user: User = Depends(get_current_user)
):
    """收藏关系库"""
    success = collect_relation_book(db, relation_book_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot collect this relation book (already collected or relation book is not public)"
        )

    return {"message": "Relation book collected successfully"}


@relation_books_router.delete("/{relation_book_id}/collect")
def uncollect_relation_book_by_id(
    *,
    db: Session = Depends(get_db),
    relation_book_id: int,
    current_user: User = Depends(get_current_user)
):
    """取消收藏关系库"""
    success = uncollect_relation_book(db, relation_book_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relation book not collected"
        )

    return {"message": "Relation book uncollected successfully"}