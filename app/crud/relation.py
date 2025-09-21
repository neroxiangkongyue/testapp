# crud/relation.py
from collections import deque

from sqlmodel import select, Session
from typing import List, Optional, Tuple

from app.models.relation import WordRelation
from app.models.word import Word
from app.schemas.word import WordRelationCreate, WordRelationUpdate, GraphPath


def create_relation(db: Session, relation: WordRelationCreate) -> WordRelation:
    """创建新关系"""
    db_relation = WordRelation.model_validate(relation)
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


def get_relation(db: Session, relation_id: int) -> Optional[WordRelation]:
    """根据ID获取关系"""
    return db.get(WordRelation, relation_id)


def get_relations_by_word(db: Session, word_id: int) -> List[WordRelation]:
    """获取单词的所有关系（出站）"""
    statement = select(WordRelation).where(WordRelation.source_id == word_id)
    return db.execute(statement).scalars().all()


def get_relations_to_word(db: Session, word_id: int) -> List[WordRelation]:
    """获取指向单词的所有关系（入站）"""
    statement = select(WordRelation).where(WordRelation.target_id == word_id)
    return db.execute(statement).scalars().all()


def update_relation(db: Session, relation_id: int, relation_update: WordRelationUpdate) -> Optional[WordRelation]:
    """更新关系"""
    db_relation = db.get(WordRelation, relation_id)
    if not db_relation:
        return None

    update_data = relation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_relation, field, value)

    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


def delete_relation(db: Session, relation_id: int) -> bool:
    """删除关系"""
    db_relation = db.get(WordRelation, relation_id)
    if not db_relation:
        return False

    db.delete(db_relation)
    db.commit()
    return True


def get_relation_by_word(db: Session, relation: WordRelationCreate) -> Optional[WordRelation]:
    statement = select(WordRelation).where(
        (WordRelation.source_id == relation.source_id) &
        (WordRelation.target_id == relation.target_id) &
        (WordRelation.relation_type == relation.relation_type)
    )
    existing_relation = db.execute(statement).scalars().first()
    return existing_relation


def get_word_relations_between(db: Session, source_id: int, target_id: int):
    return db.execute(
        select(WordRelation)
        .where(
            # or_(
            #     # 正常方向：source→target
            (WordRelation.source_id == source_id) & (WordRelation.target_id == target_id),
            # 反向方向：target→source
            # (WordRelation.source_id == target_id) & (WordRelation.target_id == source_id)
            # )
        )
    ).scalar()  # 使用 scalar() 获取单个结果


def get_word_relations(session: Session, word_id: int) -> List[Tuple[int, int, str]]:
    """获取单词的所有关系（出度和入度）"""
    # 获取出度关系
    out_relations = session.execute(
        select(WordRelation)
        .where(WordRelation.source_id == word_id)
    ).scalars().all()

    # 获取入度关系
    in_relations = session.execute(
        select(WordRelation)
        .where(WordRelation.target_id == word_id)
    ).scalars().all()

    # 格式化结果：(目标单词ID, 关系ID, 关系类型)
    relations = []
    for rel in out_relations:
        relations.append((rel.target_id, rel.id, rel.relation_type))

    for rel in in_relations:
        relations.append((rel.source_id, rel.id, rel.relation_type))

    return relations


def find_paths(
        db: Session,
        source_id: int,
        target_id: int,
        max_paths: int = 10,
        min_length: int = 1,
        max_length: int = 10
) -> List[GraphPath]:
    """查找两个单词之间的所有路径

    使用BFS算法查找从source_id到target_id的所有路径
    路径长度在min_length和max_length之间
    最多返回max_paths条路径
    """
    # 验证单词存在
    source_word = db.get(Word, source_id)
    target_word = db.get(Word, target_id)

    if not source_word or not target_word:
        raise ValueError("单词不存在")

    # 如果源和目标相同，返回空路径
    if source_id == target_id:
        return [GraphPath(path=[source_id], relations=[], length=0)]

    # 使用BFS算法查找路径
    paths = []
    queue = deque([(source_id, [source_id], [], 0)])  # (当前节点, 路径, 关系, 长度)

    while queue and len(paths) < max_paths:
        current_node, path, relations, length = queue.popleft()

        # 如果路径长度超过最大值，跳过
        if length >= max_length:
            continue

        # 获取当前节点的所有关系
        current_relations = get_word_relations(db, current_node)

        for next_node, rel_id, rel_type in current_relations:
            # 避免循环路径
            if next_node in path:
                continue

            # 创建新的路径
            new_path = path + [next_node]
            new_relations = relations + [rel_id]
            new_length = length + 1

            # 如果找到目标节点
            if next_node == target_id:
                if min_length <= new_length <= max_length:
                    paths.append(GraphPath(
                        path=new_path,
                        relations=new_relations,
                        length=new_length
                    ))
                    if len(paths) >= max_paths:
                        break
            else:
                # 将新路径加入队列
                queue.append((next_node, new_path, new_relations, new_length))

    return paths
