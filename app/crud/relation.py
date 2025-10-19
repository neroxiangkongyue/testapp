from collections import deque

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional, Dict
from datetime import datetime
from app.models.relation import WordRelation, RelationType
from app.models.word import Word
from app.schemas.relation import WordRelationCreate, WordRelationUpdate, RelationTypeCreate, RelationTypeUpdate
from app.exceptions import NotFoundException, ValidationException


def create_relation(db: Session, relation_in: WordRelationCreate) -> WordRelation:
    """创建新关系"""
    # 检查源单词和目标单词是否存在
    source_word = db.query(Word).filter(Word.id == relation_in.source_word_id).first()
    if not source_word:
        raise NotFoundException("Source word not found")

    target_word = db.query(Word).filter(Word.id == relation_in.target_word_id).first()
    if not target_word:
        raise NotFoundException("Target word not found")

    # 检查源单词和目标单词是否相同
    if relation_in.source_word_id == relation_in.target_word_id:
        raise ValidationException("Source and target words cannot be the same")

    # 检查是否已存在相同关系
    existing = db.query(WordRelation).filter(
        and_(
            WordRelation.source_word_id == relation_in.source_word_id,
            WordRelation.target_word_id == relation_in.target_word_id
        )
    ).first()

    if existing:
        raise ValidationException("Relation already exists")

    # 创建关系
    relation = WordRelation(
        source_word_id=relation_in.source_word_id,
        target_word_id=relation_in.target_word_id,
        strength=relation_in.strength,
        description=relation_in.description
    )

    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation


def get_relation(db: Session, relation_id: int) -> Optional[WordRelation]:
    """获取单个关系"""
    return db.query(WordRelation).filter(WordRelation.id == relation_id).first()


def get_relations_between_words(
        db: Session,
        source_id: int,
        target_id: int
) -> List[WordRelation]:
    """获取两个单词之间的直接关系"""
    return db.query(WordRelation).filter(
        and_(
            WordRelation.source_word_id == source_id,
            WordRelation.target_word_id == target_id
        )
    ).all()


def get_word_outgoing_relations(
        db: Session,
        word_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[WordRelation]:
    """获取单词的所有出站关系"""
    return db.query(WordRelation).filter(
        WordRelation.source_word_id == word_id
    ).offset(skip).limit(limit).all()


def get_word_incoming_relations(
        db: Session,
        word_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[WordRelation]:
    """获取单词的所有入站关系"""
    return db.query(WordRelation).filter(
        WordRelation.target_word_id == word_id
    ).offset(skip).limit(limit).all()


def get_word_all_relations(
        db: Session,
        word_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[WordRelation]:
    """获取单词的所有关系"""
    return db.query(WordRelation).filter(
        or_(
            WordRelation.source_word_id == word_id,
            WordRelation.target_word_id == word_id
        )
    ).offset(skip).limit(limit).all()


def update_relation(
        db: Session,
        relation_id: int,
        relation_in: WordRelationUpdate
) -> Optional[WordRelation]:
    """更新关系"""
    relation = get_relation(db, relation_id)
    if not relation:
        return None

    if relation_in.strength is not None:
        relation.strength = relation_in.strength

    if relation_in.description is not None:
        relation.description = relation_in.description

    relation.updated_at = datetime.utcnow()

    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation


def delete_relation(db: Session, relation_id: int) -> bool:
    """删除关系"""
    relation = get_relation(db, relation_id)
    if not relation:
        return False

    # 删除关联的类型
    db.query(RelationType).filter(RelationType.relation_id == relation_id).delete()

    # 删除关系
    db.delete(relation)
    db.commit()
    return True


def create_relation_type(db: Session, type_in: RelationTypeCreate) -> RelationType:
    """创建新关系类型"""
    # 检查关联的关系是否存在
    relation = get_relation(db, type_in.relation_id)
    if not relation:
        raise NotFoundException("Relation not found")

    # 检查类型名称是否唯一
    existing = db.query(RelationType).filter(
        RelationType.type_name == type_in.type_name
    ).first()

    if existing:
        raise ValidationException("Relation type name already exists")

    # 创建关系类型
    relation_type = RelationType(
        relation_id=type_in.relation_id,
        type_name=type_in.type_name,
        category=type_in.category,
        description=type_in.description
    )

    db.add(relation_type)
    db.commit()
    db.refresh(relation_type)
    return relation_type


def get_relation_type(db: Session, type_id: int) -> Optional[RelationType]:
    """获取关系类型详情"""
    return db.query(RelationType).filter(RelationType.id == type_id).first()


def get_relation_types_by_relation(
        db: Session,
        relation_id: int
) -> List[RelationType]:
    """获取关系关联的所有类型"""
    return db.query(RelationType).filter(
        RelationType.relation_id == relation_id
    ).all()


def update_relation_type(
        db: Session,
        type_id: int,
        type_in: RelationTypeUpdate
) -> Optional[RelationType]:
    """更新关系类型"""
    relation_type = get_relation_type(db, type_id)
    if not relation_type:
        return None

    if type_in.type_name is not None:
        # 检查新名称是否唯一
        existing = db.query(RelationType).filter(
            and_(
                RelationType.type_name == type_in.type_name,
                RelationType.id != type_id
            )
        ).first()

        if existing:
            raise ValidationException("Relation type name already exists")

        relation_type.type_name = type_in.type_name

    if type_in.category is not None:
        relation_type.category = type_in.category

    if type_in.description is not None:
        relation_type.description = type_in.description

    relation_type.updated_at = datetime.utcnow()

    db.add(relation_type)
    db.commit()
    db.refresh(relation_type)
    return relation_type


def delete_relation_type(db: Session, type_id: int) -> bool:
    """删除关系类型"""
    relation_type = get_relation_type(db, type_id)
    if not relation_type:
        return False

    db.delete(relation_type)
    db.commit()
    return True


def get_word_graph(
        db: Session,
        word_id: int,
        max_level: int = 3,
        max_nodes: int = 100
) -> Dict[str, List]:
    """获取单词的关系图数据"""
    # 验证单词是否存在
    center_word = db.query(Word).filter(Word.id == word_id).first()
    if not center_word:
        raise NotFoundException("Center word not found")

    # 存储节点和边
    nodes = []
    edges = []

    # 添加中心节点
    nodes.append({
        "id": word_id,
        "word": center_word.word,
        "level": 0
    })

    # 使用队列进行 BFS
    queue = deque()
    queue.append((word_id, 0))  # (单词ID, 层级)

    visited = {word_id}

    while queue and len(nodes) < max_nodes:
        current_id, level = queue.popleft()

        # 如果超过最大层级
        if level >= max_level:
            continue

        # 获取当前单词的所有关系
        relations = get_word_all_relations(db, current_id, 0, 100)

        for relation in relations:
            # 确定邻居节点
            if relation.source_word_id == current_id:
                neighbor_id = relation.target_word_id
            else:
                neighbor_id = relation.source_word_id

            # 如果邻居节点已访问过，只添加边
            if neighbor_id in visited:
                edges.append({
                    "source": current_id,
                    "target": neighbor_id,
                    "relation_id": relation.id,
                    "strength": relation.strength
                })
                continue

            # 获取邻居单词
            neighbor_word = db.query(Word).filter(Word.id == neighbor_id).first()
            if not neighbor_word:
                continue

            # 添加新节点
            nodes.append({
                "id": neighbor_id,
                "word": neighbor_word.word,
                "level": level + 1
            })

            # 添加边
            edges.append({
                "source": current_id,
                "target": neighbor_id,
                "relation_id": relation.id,
                "strength": relation.strength
            })

            # 标记为已访问
            visited.add(neighbor_id)

            # 添加邻居到队列
            queue.append((neighbor_id, level + 1))

    return {
        "nodes": nodes,
        "edges": edges
    }
