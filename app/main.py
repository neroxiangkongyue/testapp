# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_tables

# 导入所有API端点
from api.endpoints.word import router as words_router
from api.endpoints.definition import router as definitions_router
from api.endpoints.example import router as examples_router
from api.endpoints.form import router as forms_router
from api.endpoints.pronunciation import router as pronunciations_router
from api.endpoints.relation import router as relations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_db_tables()
    yield
    # 关闭时清理资源（如果需要）

app = FastAPI(
    title="单词管理系统",
    description="一个用于管理单词及其关系的API",
    version="1.0.0",
    lifespan=lifespan
)

# 包含所有路由
app.include_router(words_router)
app.include_router(definitions_router)
app.include_router(examples_router)
app.include_router(forms_router)
app.include_router(pronunciations_router)
app.include_router(relations_router)

@app.get("/")
def read_root():
    return {"message": "欢迎使用单词管理系统API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8082, reload=True)
