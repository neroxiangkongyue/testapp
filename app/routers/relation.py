from collections import deque
from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.crud.relation import (
    create_relation, get_relation, get_relations_between_words,
    get_word_outgoing_relations, get_word_incoming_relations, get_word_all_relations,
    update_relation, delete_relation,
    create_relation_type, get_relation_type, get_relation_types_by_relation,
    update_relation_type, delete_relation_type, get_word_graph
)
from app.crud.word import get_word
from app.database import get_db
from app.exceptions import NotFoundException
from app.models import Word
from app.models.user import User
from app.schemas.note import WordBrief
from app.schemas.relation import (
    WordRelationCreate, WordRelation, WordRelationWithWords, WordRelationUpdate,
    RelationTypeCreate, RelationType, RelationTypeUpdate, GraphResponse, GraphEdge, GraphNode, PathResponse, PathNode
)

relations_router = APIRouter(prefix="/relations", tags=["relations"])


# 单词关系路由
@relations_router.post("/", response_model=WordRelation, status_code=status.HTTP_201_CREATED)
def create_new_relation(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        relation_in: WordRelationCreate
):
    """创建新关系"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    try:
        relation = create_relation(db, relation_in)
        return relation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@relations_router.get("/{relation_id}", response_model=WordRelationWithWords)
def read_relation(
        *,
        db: Session = Depends(get_db),
        relation_id: int
):
    """获取关系详情"""
    relation = get_relation(db, relation_id)
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found"
        )

    # 获取单词信息
    source_word = get_word(db, relation.source_word_id)
    target_word = get_word(db, relation.target_word_id)

    if not source_word or not target_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Related word not found"
        )

    # 获取关系类型
    relation_types = get_relation_types_by_relation(db, relation_id)

    return WordRelationWithWords(
        id=relation.id,
        source_word_id=relation.source_word_id,
        target_word_id=relation.target_word_id,
        strength=relation.strength,
        description=relation.description,
        created_at=relation.created_at,
        updated_at=relation.updated_at,
        source_word=WordBrief(
            id=source_word.id,
            word=source_word.word,
            normalized_word=source_word.normalized_word,
            length=source_word.length
        ),
        target_word=WordBrief(
            id=target_word.id,
            word=target_word.word,
            normalized_word=target_word.normalized_word,
            length=target_word.length
        ),
        relation_types=relation_types
    )


@relations_router.get("/between-words", response_model=List[WordRelation])
def read_relations_between_words(
        *,
        db: Session = Depends(get_db),
        source_id: int = Query(..., description="源单词ID"),
        target_id: int = Query(..., description="目标单词ID")
):
    """获取两个单词之间的直接关系"""
    relations = get_relations_between_words(db, source_id, target_id)
    return relations


@relations_router.get("/word/{word_id}/outgoing", response_model=List[WordRelation])
def read_word_outgoing_relations(
        *,
        db: Session = Depends(get_db),
        word_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
):
    """获取单词的所有出站关系"""
    relations = get_word_outgoing_relations(db, word_id, skip, limit)
    return relations


@relations_router.get("/word/{word_id}/incoming", response_model=List[WordRelation])
def read_word_incoming_relations(
        *,
        db: Session = Depends(get_db),
        word_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
):
    """获取单词的所有入站关系"""
    relations = get_word_incoming_relations(db, word_id, skip, limit)
    return relations


@relations_router.get("/word/{word_id}/all", response_model=List[WordRelation])
def read_word_all_relations(
        *,
        db: Session = Depends(get_db),
        word_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
):
    """获取单词的所有关系"""
    relations = get_word_all_relations(db, word_id, skip, limit)
    return relations


@relations_router.put("/{relation_id}", response_model=WordRelation)
def update_relation_details(
        *,
        db: Session = Depends(get_db),
        relation_id: int,
        relation_in: WordRelationUpdate,
        current_user: User = Depends(get_current_user)
):
    """更新关系"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    try:
        relation = update_relation(db, relation_id, relation_in)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found"
            )
        return relation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@relations_router.delete("/{relation_id}")
def delete_relation_by_id(
        *,
        db: Session = Depends(get_db),
        relation_id: int,
        current_user: User = Depends(get_current_user)
):
    """删除关系"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    success = delete_relation(db, relation_id)
    if success:
        return {"message": "Relation deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found"
        )


# 关系类型路由
@relations_router.post("/types", response_model=RelationType, status_code=status.HTTP_201_CREATED)
def create_new_relation_type(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        type_in: RelationTypeCreate
):
    """创建新关系类型"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    try:
        relation_type = create_relation_type(db, type_in)
        return relation_type
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@relations_router.get("/types/{type_id}", response_model=RelationType)
def read_relation_type(
        *,
        db: Session = Depends(get_db),
        type_id: int
):
    """获取关系类型详情"""
    relation_type = get_relation_type(db, type_id)
    if not relation_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation type not found"
        )
    return relation_type


@relations_router.get("/relations/{relation_id}/types", response_model=List[RelationType])
def read_relation_types(
        *,
        db: Session = Depends(get_db),
        relation_id: int
):
    """获取关系关联的所有类型"""
    relation_types = get_relation_types_by_relation(db, relation_id)
    return relation_types


@relations_router.put("/types/{type_id}", response_model=RelationType)
def update_relation_type_details(
        *,
        db: Session = Depends(get_db),
        type_id: int,
        type_in: RelationTypeUpdate,
        current_user: User = Depends(get_current_user)
):
    """更新关系类型"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    try:
        relation_type = update_relation_type(db, type_id, type_in)
        if not relation_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation type not found"
            )
        return relation_type
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@relations_router.delete("/types/{type_id}")
def delete_relation_type_by_id(
        *,
        db: Session = Depends(get_db),
        type_id: int,
        current_user: User = Depends(get_current_user)
):
    """删除关系类型"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    success = delete_relation_type(db, type_id)
    if success:
        return {"message": "Relation type deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation type not found"
        )


@relations_router.get("/paths", response_model=List[PathResponse])
def find_paths(
        *,
        db: Session = Depends(get_db),
        start_id: int = Query(..., description="起始单词ID"),
        end_id: int = Query(..., description="目标单词ID"),
        max_length: int = Query(5, ge=1, le=10, description="最大路径长度"),
        max_paths: int = Query(10, ge=1, le=50, description="最大返回路径数")
):
    """查找两个单词之间的路径"""
    try:
        paths = find_paths_between_words(db, start_id, end_id, max_length, max_paths)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not paths:
        return []

    # 构建响应
    response = []
    for path, total_strength in paths:
        path_nodes = []
        length = 0

        # 构建路径节点
        for i in range(len(path) - 1):
            word_id = path[i]
            next_word_id = path[i + 1]

            # 获取单词
            word = get_word(db, word_id)
            if not word:
                continue

            # 获取关系
            relations = get_relations_between_words(db, word_id, next_word_id)
            relation = relations[0] if relations else None

            path_nodes.append(PathNode(
                word_id=word_id,
                word=WordBrief(
                    id=word.id,
                    word=word.word,
                    normalized_word=word.normalized_word,
                    length=word.length
                ),
                relation_id=relation.id if relation else None,
                relation=relation if relation else None
            ))

            if relation:
                length += 1

        # 添加最后一个节点
        last_word = get_word(db, path[-1])
        if last_word:
            path_nodes.append(PathNode(
                word_id=path[-1],
                word=WordBrief(
                    id=last_word.id,
                    word=last_word.word,
                    normalized_word=last_word.normalized_word,
                    length=last_word.length
                ),
                relation_id=None,
                relation=None
            ))

        response.append(PathResponse(
            path=path_nodes,
            total_strength=total_strength,
            length=length
        ))

    return response


@relations_router.get("/graph", response_model=GraphResponse)
def get_word_relation_graph(
        *,
        db: Session = Depends(get_db),
        word_id: int = Query(..., description="中心单词ID"),
        max_level: int = Query(3, ge=1, le=5, description="最大层级"),
        max_nodes: int = Query(100, ge=1, le=200, description="最大节点数")
):
    """获取单词的关系图数据"""
    try:
        graph_data = get_word_graph(db, word_id, max_level, max_nodes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 构建响应
    nodes = []
    for node in graph_data['nodes']:
        nodes.append(GraphNode(
            id=node['id'],
            word=node['word'],
            level=node['level']
        ))

    edges = []
    for edge in graph_data['edges']:
        edges.append(GraphEdge(
            source=edge['source'],
            target=edge['target'],
            relation_id=edge['relation_id'],
            strength=edge['strength']
        ))

    return GraphResponse(nodes=nodes, edges=edges)


def find_paths_between_words(
        db: Session,
        start_id: int,
        end_id: int,
        max_length: int = 5,
        max_paths: int = 10
) -> List[Tuple[List[int], float]]:
    """查找两个单词之间的路径"""
    # 验证单词是否存在
    start_word = db.query(Word).filter(Word.id == start_id).first()
    if not start_word:
        raise NotFoundException("Start word not found")

    end_word = db.query(Word).filter(Word.id == end_id).first()
    if not end_word:
        raise NotFoundException("End word not found")

    # 使用 BFS 算法查找路径
    paths = []
    queue = deque()
    queue.append(([start_id], 1.0))  # (路径, 总强度)

    visited = set()

    while queue and len(paths) < max_paths:
        path, total_strength = queue.popleft()
        current_id = path[-1]

        # 如果找到目标单词
        if current_id == end_id:
            paths.append((path, total_strength))
            continue

        # 如果路径长度超过限制
        if len(path) >= max_length:
            continue

        # 标记当前节点已访问
        visited.add(current_id)

        # 获取当前单词的所有关系
        relations = get_word_all_relations(db, current_id, 0, 100)

        for relation in relations:
            # 确定邻居节点
            if relation.source_word_id == current_id:
                neighbor_id = relation.target_word_id
            else:
                neighbor_id = relation.source_word_id

            # 避免循环
            if neighbor_id in path:
                continue

            # 计算新路径的总强度
            new_strength = total_strength * relation.strength

            # 添加新路径到队列
            new_path = path + [neighbor_id]
            queue.append((new_path, new_strength))

    return paths
