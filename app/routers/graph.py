# 图谱查询端点
from fastapi import APIRouter

router = APIRouter()

@router.get("/graph/{word}")
def get_word_graph(word: str):
    # 实现获取单词图谱逻辑
    pass

@router.get("/path")
def find_path(source: str, target: str):
    # 实现查找路径逻辑
    pass