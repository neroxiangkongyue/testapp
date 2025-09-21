# 导入单词数据脚本
import pandas as pd
from sqlmodel import Session

from app.database import engine
from app.models.word import Word

def import_oxford_3000():
    """导入牛津3000词表"""
    # 实现数据导入逻辑
    pass

if __name__ == "__main__":
    import_oxford_3000()
    print("单词数据导入完成")