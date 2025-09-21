# 初始化数据库脚本
from app.database import create_db_and_tables

if __name__ == "__main__":
    create_db_and_tables()
    print("数据库初始化完成")