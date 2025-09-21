# api/endpoints/relation.py
from collections import deque

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional, Dict, Any

from app.crud.word import get_word
from app.database import get_db
from app.models.word import Word
from app.schemas.word import WordRelationCreate, WordRelationRead, WordRelationUpdate, GraphPath
from app.crud.relation import (
    create_relation, get_relation, get_relations_by_word,
    get_relations_to_word, update_relation, delete_relation, get_relation_by_word, get_word_relations_between,
    get_word_relations, find_paths
)

router = APIRouter(prefix="/relations", tags=["relations"])


@router.post("/", response_model=WordRelationRead)
def create_relation_endpoint(relation: WordRelationCreate, db: Session = Depends(get_db)):
    """创建新关系"""
    # 检查是否已存在相同的关系
    source = get_word(db, relation.source_id)
    target = get_word(db, relation.target_id)
    if source is not None or target is not None:
        raise HTTPException(status_code=400, detail="单词不存在")
    existing_relation = get_relation_by_word(db, relation)
    if existing_relation:
        raise HTTPException(status_code=400, detail="关系已存在")

    return create_relation(db, relation)


@router.get("/from/{word_id}", response_model=List[WordRelationRead])
def read_relations_from_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """获取单词的所有出站关系"""
    return get_relations_by_word(db, word_id)


@router.get("/to/{word_id}", response_model=List[WordRelationRead])
def read_relations_to_word_endpoint(word_id: int, db: Session = Depends(get_db)):
    """获取单词的所有入站关系"""
    return get_relations_to_word(db, word_id)


@router.get("/{relation_id}", response_model=WordRelationRead)
def read_relation_endpoint(relation_id: int, db: Session = Depends(get_db)):
    """根据ID获取关系"""
    relation = get_relation(db, relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="关系未找到")
    return relation


@router.put("/{relation_id}", response_model=WordRelationRead)
def update_relation_endpoint(relation_id: int, relation_update: WordRelationUpdate, db: Session = Depends(get_db)):
    """更新关系"""
    relation = update_relation(db, relation_id, relation_update)
    if not relation:
        raise HTTPException(status_code=404, detail="关系未找到")
    return relation


@router.delete("/{relation_id}")
def delete_relation_endpoint(relation_id: int, db: Session = Depends(get_db)):
    """删除关系"""
    success = delete_relation(db, relation_id)
    if not success:
        raise HTTPException(status_code=404, detail="关系未找到")
    return {"message": "关系已删除"}


@router.get("/between/", response_model=WordRelationRead)
def get_relation_between_words(
        source_id: int,
        target_id: int,
        db: Session = Depends(get_db)
):
    """获取两个单词之间的直接关系"""
    relation = get_word_relations_between(db, source_id, target_id)
    if not relation:
        raise HTTPException(
            status_code=404,
            detail="未找到这两个单词之间的直接关系"
        )
    return relation


@router.get("/paths/", response_model=List[GraphPath])
def find_paths_between_words(
        source_id: int = Query(..., description="起始单词ID"),
        target_id: int = Query(..., description="目标单词ID"),
        max_paths: Optional[int] = Query(10, description="最大返回路径数量"),
        min_length: Optional[int] = Query(1, description="最小路径长度"),
        max_length: Optional[int] = Query(10, description="最大路径长度"),
        db: Session = Depends(get_db)
):
    """查找两个单词之间的路径"""
    try:
        paths = find_paths(db, source_id, target_id, max_paths, min_length, max_length)
        if not paths:
            raise HTTPException(
                status_code=404,
                detail=f"在 {max_length} 步内未找到路径"
            )
        return paths
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查找路径失败: {str(e)}"
        )


@router.get("/relations/{word_id}")
def get_word_relations_graph(
        word_id: int,
        depth: int = Query(1, description="关系深度"),
        max_edges: int = Query(10, description="每个节点最大边数"),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取单词的关系图数据（极简版，只返回ID）"""
    # 验证单词是否存在
    word = db.get(Word, word_id)
    if not word:
        raise HTTPException(status_code=404, detail="单词未找到")

    # 使用BFS获取指定深度的关系图
    node_ids = {word_id}  # 使用集合避免重复节点
    edges = []  # 边列表，只包含关系ID和连接信息
    seen_edges = set()  # 用于跟踪已处理的边，避免重复

    # BFS队列: (节点ID, 当前深度)
    queue = deque([(word_id, 0)])
    visited = {word_id}

    while queue:
        current_id, current_depth = queue.popleft()

        # 如果达到最大深度，停止扩展
        if current_depth >= depth:
            continue

        # 获取当前节点的关系
        relations = get_word_relations(db, current_id)

        # 限制每个节点的边数
        if 0 < max_edges < len(relations):
            relations = relations[:max_edges]

        for target_id, rel_id, rel_type in relations:
            # 验证目标单词是否存在
            target_word = db.get(Word, target_id)
            if not target_word:
                continue

            # 添加目标节点ID
            node_ids.add(target_id)

            # 创建边的唯一标识符（考虑方向）
            edge_key = f"{current_id}-{target_id}"
            reverse_edge_key = f"{target_id}-{current_id}"

            # 检查是否已存在相同或相反的边
            if edge_key in seen_edges or reverse_edge_key in seen_edges:
                continue

            # 记录这条边
            seen_edges.add(edge_key)

            # 添加边（只包含关系ID和连接信息）
            edges.append({
                "id": rel_id,
                "source": current_id,
                "target": target_id,
            })

            # 如果目标节点未访问过，加入队列
            if target_id not in visited:
                visited.add(target_id)
                queue.append((target_id, current_depth + 1))

    return {
        "node_ids": list(node_ids),  # 只返回节点ID列表
        "edges": edges  # 只返回边的基本连接信息
    }
