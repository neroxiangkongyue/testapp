import os
from pathlib import Path


def create_project_structure(base_path):
    """创建后端项目结构"""

    # 定义项目结构
    structure = {
        "app": {
            "__init__.py": "",
            "main.py": "# FastAPI应用入口点\nfrom fastapi import FastAPI\n\napp = FastAPI(title=\"英语学习图谱API\")\n\n# 包含路由\n# from app.api.endpoints import words, relations, auth, ...\n\n@app.get(\"/\")\nasync def root():\n    return {\"message\": \"英语学习图谱API\"}",
            "core": {
                "__init__.py": "",
                "config.py": "# 应用配置\nfrom pydantic_settings import BaseSettings\n\nclass Settings(BaseSettings):\n    database_url: str = \"sqlite:///./english_graph.db\"\n    secret_key: str = \"your-secret-key-here\"\n    \n    class Config:\n        env_file = \".env\"\n\nsettings = Settings()",
                "security.py": "# 安全相关函数\nfrom passlib.context import CryptContext\n\npwd_context = CryptContext(schemes=[\"bcrypt\"], deprecated=\"auto\")\n\ndef verify_password(plain_password, hashed_password):\n    return pwd_context.verify(plain_password, hashed_password)\n\ndef get_password_hash(password):\n    return pwd_context.hash(password)",
                "dependencies.py": "# 依赖注入\nfrom fastapi import Depends, HTTPException, status\nfrom sqlmodel import Session\n\nfrom app.core.security import verify_password\nfrom app.database import get_db\nfrom app.models.user import User\nfrom app.crud.user import get_user_by_username\n\n# 示例依赖函数\ndef get_current_user():\n    # 实现获取当前用户逻辑\n    pass",
            },
            "models": {
                "__init__.py": "",
                "user.py": "# 用户模型\nfrom sqlmodel import SQLModel, Field\nfrom typing import Optional\nfrom datetime import datetime\n\nclass User(SQLModel, table=True):\n    id: Optional[int] = Field(default=None, primary_key=True)\n    username: str = Field(unique=True, index=True)\n    openid: str = Field(unique=True, index=True)  # 微信用户的唯一标识\n    avatar_url: Optional[str] = None\n    created_at: datetime = Field(default_factory=datetime.utcnow)",
                "word.py": "# 单词模型\nfrom sqlmodel import SQLModel, Field\nfrom typing import Optional\n\nclass Word(SQLModel, table=True):\n    id: Optional[int] = Field(default=None, primary_key=True)\n    spelling: str = Field(unique=True, index=True)\n    ipa: str  # 音标\n    meaning: str  # 释义\n    frequency: Optional[int] = None  # 词频\n    pos: Optional[str] = None  # 词性\n    is_public: bool = Field(default=False)  # 是否为公开词库",
                "relation.py": "# 关系模型\nfrom sqlmodel import SQLModel, Field, Relationship\nfrom typing import Optional\nfrom datetime import datetime\n\nclass RelationType(SQLModel, table=True):\n    id: Optional[int] = Field(default=None, primary_key=True)\n    name: str = Field(unique=True)  # 关系类型名称\n    color: Optional[str] = None  # 在图谱中显示的颜色\n\nclass GlobalRelation(SQLModel, table=True):\n    id: Optional[int] = Field(default=None, primary_key=True)\n    source_id: int = Field(foreign_key=\"word.id\")\n    target_id: int = Field(foreign_key=\"word.id\")\n    relation_type_id: int = Field(foreign_key=\"relationtype.id\")\n    weight: float = Field(default=1.0)  # 关系权重\n    created_by: Optional[int] = Field(foreign_key=\"user.id\", default=None)\n    is_approved: bool = Field(default=False)  # 是否审核通过\n\nclass UserRelation(SQLModel, table=True):\n    id: Optional[int] = Field(default=None, primary_key=True)\n    source_id: int = Field(foreign_key=\"word.id\")\n    target_id: int = Field(foreign_key=\"word.id\")\n    relation_type_id: int = Field(foreign_key=\"relationtype.id\")\n    weight: float = Field(default=1.0)  # 关系权重\n    user_id: int = Field(foreign_key=\"user.id\")  # 所属用户\n    notes: Optional[str] = None  # 用户笔记\n    created_at: datetime = Field(default_factory=datetime.utcnow)",
                "contribution.py": "# 用户贡献模型\nfrom sqlmodel import SQLModel, Field\nfrom typing import Optional\nfrom datetime import datetime\nfrom enum import Enum\n\nclass ContributionType(str, Enum):\n    ADD_WORD = \"add_word\"\n    UPDATE_WORD = \"update_word\"\n    ADD_RELATION = \"add_relation\"\n    UPDATE_RELATION = \"update_relation\"\n\nclass ContributionStatus(str, Enum):\n    PENDING = \"pending\"\n    APPROVED = \"approved\"\n    REJECTED = \"rejected\"\n\nclass UserContribution(SQLModel, table=True):\n    id: Optional[int] = Field(default=None, primary_key=True)\n    type: ContributionType  # 贡献类型\n    data: str  # JSON字段，存储提交的详细数据\n    status: ContributionStatus = Field(default=ContributionStatus.PENDING)\n    submitted_by: int = Field(foreign_key=\"user.id\")  # 提交者\n    submitted_at: datetime = Field(default_factory=datetime.utcnow)\n    reviewed_by: Optional[int] = Field(foreign_key=\"user.id\", default=None)  # 审核人\n    reviewed_at: Optional[datetime] = None  # 审核时间\n    feedback: Optional[str] = None  # 审核反馈",
            },
            "schemas": {
                "__init__.py": "",
                "user.py": "# 用户相关的请求/响应模型\nfrom pydantic import BaseModel\nfrom typing import Optional\nfrom datetime import datetime\n\nclass UserBase(BaseModel):\n    username: str\n\nclass UserCreate(UserBase):\n    password: str\n\nclass User(UserBase):\n    id: int\n    avatar_url: Optional[str]\n    created_at: datetime\n    \n    class Config:\n        from_attributes = True\n\nclass Token(BaseModel):\n    access_token: str\n    token_type: str",
                "word.py": "# 单词相关的请求/响应模型\nfrom pydantic import BaseModel\nfrom typing import Optional\n\nclass WordBase(BaseModel):\n    spelling: str\n    ipa: str\n    meaning: str\n\nclass WordCreate(WordBase):\n    pass\n\nclass Word(WordBase):\n    id: int\n    frequency: Optional[int]\n    pos: Optional[str]\n    is_public: bool\n    \n    class Config:\n        from_attributes = True",
                "relation.py": "# 关系相关的请求/响应模型\nfrom pydantic import BaseModel\nfrom typing import Optional\n\nclass RelationBase(BaseModel):\n    source_id: int\n    target_id: int\n    relation_type_id: int\n    weight: Optional[float] = 1.0\n\nclass RelationCreate(RelationBase):\n    pass\n\nclass Relation(RelationBase):\n    id: int\n    \n    class Config:\n        from_attributes = True",
                "contribution.py": "# 贡献相关的请求/响应模型\nfrom pydantic import BaseModel\nfrom typing import Optional\nfrom datetime import datetime\nfrom app.models.contribution import ContributionType, ContributionStatus\n\nclass ContributionBase(BaseModel):\n    type: ContributionType\n    data: str\n\nclass ContributionCreate(ContributionBase):\n    pass\n\nclass Contribution(ContributionBase):\n    id: int\n    status: ContributionStatus\n    submitted_by: int\n    submitted_at: datetime\n    reviewed_by: Optional[int]\n    reviewed_at: Optional[datetime]\n    feedback: Optional[str]\n    \n    class Config:\n        from_attributes = True",
            },
            "api": {
                "__init__.py": "",
                "endpoints": {
                    "__init__.py": "",
                    "auth.py": "# 认证相关端点\nfrom fastapi import APIRouter, Depends, HTTPException, status\nfrom sqlmodel import Session\n\nfrom app.database import get_db\nfrom app.schemas.user import UserCreate, User, Token\nfrom app.crud.user import create_user, get_user_by_username\nfrom app.core.security import get_password_hash, verify_password\n\nrouter = APIRouter()\n\n@router.post(\"/register\", response_model=User)\ndef register(user: UserCreate, db: Session = Depends(get_db)):\n    # 实现用户注册逻辑\n    pass\n\n@router.post(\"/login\", response_model=Token)\ndef login():\n    # 实现用户登录逻辑\n    pass",
                    "words.py": "# 单词相关端点\nfrom fastapi import APIRouter, Depends, HTTPException\nfrom sqlmodel import Session\n\nfrom app.database import get_db\nfrom app.schemas.word import Word, WordCreate\nfrom app.crud.word import get_word, create_word, get_words\n\nrouter = APIRouter()\n\n@router.get(\"/words\", response_model=list[Word])\ndef read_words(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):\n    words = get_words(db, skip=skip, limit=limit)\n    return words\n\n@router.get(\"/words/{word_id}\", response_model=Word)\ndef read_word(word_id: int, db: Session = Depends(get_db)):\n    db_word = get_word(db, word_id=word_id)\n    if db_word is None:\n        raise HTTPException(status_code=404, detail=\"Word not found\")\n    return db_word\n\n@router.post(\"/words\", response_model=Word)\ndef create_new_word(word: WordCreate, db: Session = Depends(get_db)):\n    return create_word(db=db, word=word)",
                    "relations.py": "# 关系相关端点\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/relations\")\ndef read_relations():\n    # 实现获取关系逻辑\n    pass\n\n@router.post(\"/relations\")\ndef create_relation():\n    # 实现创建关系逻辑\n    pass",
                    "graph.py": "# 图谱查询端点\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/graph/{word}\")\ndef get_word_graph(word: str):\n    # 实现获取单词图谱逻辑\n    pass\n\n@router.get(\"/path\")\ndef find_path(source: str, target: str):\n    # 实现查找路径逻辑\n    pass",
                    "contributions.py": "# 用户贡献端点\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/contributions\")\ndef read_contributions():\n    # 实现获取贡献列表逻辑\n    pass\n\n@router.post(\"/contributions\")\ndef create_contribution():\n    # 实现创建贡献逻辑\n    pass",
                    "admin.py": "# 管理员审核端点\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/admin/contributions\")\ndef admin_read_contributions():\n    # 实现管理员获取贡献列表逻辑\n    pass\n\n@router.put(\"/admin/contributions/{contribution_id}\")\ndef review_contribution(contribution_id: int):\n    # 实现审核贡献逻辑\n    pass",
                },
                "deps.py": "# 路由依赖项\nfrom fastapi import Depends, HTTPException, status\nfrom sqlmodel import Session\n\nfrom app.database import get_db\n\n# 示例依赖函数\ndef get_db_session():\n    # 实现获取数据库会话逻辑\n    pass",
            },
            "crud": {
                "__init__.py": "",
                "user.py": "# 用户CRUD操作\nfrom sqlmodel import Session, select\nfrom app.models.user import User\nfrom app.schemas.user import UserCreate\nfrom app.core.security import get_password_hash\n\ndef get_user(db: Session, user_id: int):\n    return db.exec(select(User).where(User.id == user_id)).first()\n\ndef get_user_by_username(db: Session, username: str):\n    return db.exec(select(User).where(User.username == username)).first()\n\ndef get_users(db: Session, skip: int = 0, limit: int = 100):\n    return db.exec(select(User).offset(skip).limit(limit)).all()\n\ndef create_user(db: Session, user: UserCreate):\n    hashed_password = get_password_hash(user.password)\n    db_user = User(username=user.username, hashed_password=hashed_password)\n    db.add(db_user)\n    db.commit()\n    db.refresh(db_user)\n    return db_user",
                "word.py": "# 单词CRUD操作\nfrom sqlmodel import Session, select\nfrom app.models.word import Word\nfrom app.schemas.word import WordCreate\n\ndef get_word(db: Session, word_id: int):\n    return db.exec(select(Word).where(Word.id == word_id)).first()\n\ndef get_word_by_spelling(db: Session, spelling: str):\n    return db.exec(select(Word).where(Word.spelling == spelling)).first()\n\ndef get_words(db: Session, skip: int = 0, limit: int = 100):\n    return db.exec(select(Word).offset(skip).limit(limit)).all()\n\ndef create_word(db: Session, word: WordCreate):\n    db_word = Word(**word.dict())\n    db.add(db_word)\n    db.commit()\n    db.refresh(db_word)\n    return db_word",
                "relation.py": "# 关系CRUD操作\nfrom sqlmodel import Session, select\nfrom app.models.relation import GlobalRelation, UserRelation\n\ndef get_global_relations(db: Session, skip: int = 0, limit: int = 100):\n    return db.exec(select(GlobalRelation).offset(skip).limit(limit)).all()\n\ndef get_user_relations(db: Session, user_id: int, skip: int = 0, limit: int = 100):\n    return db.exec(select(UserRelation).where(UserRelation.user_id == user_id).offset(skip).limit(limit)).all()\n\ndef create_global_relation(db: Session, relation):\n    db_relation = GlobalRelation(**relation.dict())\n    db.add(db_relation)\n    db.commit()\n    db.refresh(db_relation)\n    return db_relation\n\ndef create_user_relation(db: Session, relation):\n    db_relation = UserRelation(**relation.dict())\n    db.add(db_relation)\n    db.commit()\n    db.refresh(db_relation)\n    return db_relation",
                "contribution.py": "# 贡献CRUD操作\nfrom sqlmodel import Session, select\nfrom app.models.contribution import UserContribution\n\ndef get_contribution(db: Session, contribution_id: int):\n    return db.exec(select(UserContribution).where(UserContribution.id == contribution_id)).first()\n\ndef get_contributions(db: Session, skip: int = 0, limit: int = 100):\n    return db.exec(select(UserContribution).offset(skip).limit(limit)).all()\n\ndef create_contribution(db: Session, contribution):\n    db_contribution = UserContribution(**contribution.dict())\n    db.add(db_contribution)\n    db.commit()\n    db.refresh(db_contribution)\n    return db_contribution",
            },
            "services": {
                "__init__.py": "",
                "auth.py": "# 认证服务\nfrom jose import JWTError, jwt\nfrom datetime import datetime, timedelta\n\nfrom app.core.config import settings\n\ndef create_access_token(data: dict, expires_delta: timedelta = None):\n    # 实现创建访问令牌逻辑\n    pass\n\ndef verify_token(token: str):\n    # 实现验证令牌逻辑\n    pass",
                "graph.py": "# 图谱算法服务\nfrom typing import List, Dict, Any\n\ndef find_shortest_path(graph: Dict[str, List[str]], start: str, end: str) -> List[str]:\n    \"\"\"使用BFS算法查找最短路径\"\"\"\n    # 实现BFS算法\n    pass\n\ndef get_word_graph_data(word: str, user_id: int = None) -> Dict[str, Any]:\n    \"\"\"获取单词的图谱数据\"\"\"\n    # 实现获取图谱数据逻辑\n    pass",
                "import_data.py": "# 数据导入服务\ndef import_oxford_3000():\n    \"\"\"导入牛津3000词表\"\"\"\n    # 实现数据导入逻辑\n    pass\n\ndef import_wordnet_data():\n    \"\"\"导入WordNet数据\"\"\"\n    # 实现数据导入逻辑\n    pass",
            },
            "database.py": "# 数据库连接和引擎配置\nfrom sqlmodel import SQLModel, create_engine, Session\nfrom app.core.config import settings\n\n# 创建数据库引擎\nengine = create_engine(settings.database_url, echo=True)\n\ndef create_db_and_tables():\n    \"\"\"创建数据库和表\"\"\"\n    SQLModel.metadata.create_all(engine)\n\ndef get_db():\n    \"\"\"获取数据库会话\"\"\"\n    with Session(engine) as session:\n        yield session",
        },
        "tests": {
            "__init__.py": "",
            "conftest.py": "# pytest配置和fixture\nimport pytest\nfrom fastapi.testclient import TestClient\nfrom sqlmodel import SQLModel, Session, create_engine\nfrom sqlmodel.pool import StaticPool\n\nfrom app.main import app\nfrom app.database import get_db\n\n@pytest.fixture(name=\"session\")\ndef session_fixture():\n    engine = create_engine(\n        \"sqlite://\",\n        connect_args={\"check_same_thread\": False},\n        poolclass=StaticPool,\n    )\n    SQLModel.metadata.create_all(engine)\n    with Session(engine) as session:\n        yield session\n\n@pytest.fixture(name=\"client\")\ndef client_fixture(session: Session):\n    def get_session_override():\n        return session\n    \n    app.dependency_overrides[get_db] = get_session_override\n    client = TestClient(app)\n    yield client\n    app.dependency_overrides.clear()",
            "test_api": {
                "__init__.py": "",
                "test_words.py": "# 单词API测试\nfrom fastapi.testclient import TestClient\n\ndef test_read_words():\n    # 实现读取单词测试\n    pass\n\ndef test_read_word():\n    # 实现读取单个单词测试\n    pass",
                "test_auth.py": "# 认证API测试\nfrom fastapi.testclient import TestClient\n\ndef test_register():\n    # 实现注册测试\n    pass\n\ndef test_login():\n    # 实现登录测试\n    pass",
            },
            "test_services": {
                "__init__.py": "",
                "test_graph.py": "# 图谱服务测试\ndef test_find_shortest_path():\n    # 实现最短路径算法测试\n    pass",
            },
        },
        "scripts": {
            "init_db.py": "# 初始化数据库脚本\nfrom app.database import create_db_and_tables\n\nif __name__ == \"__main__\":\n    create_db_and_tables()\n    print(\"数据库初始化完成\")",
            "import_words.py": "# 导入单词数据脚本\nimport pandas as pd\nfrom sqlmodel import Session\n\nfrom app.database import engine\nfrom app.models.word import Word\n\ndef import_oxford_3000():\n    \"\"\"导入牛津3000词表\"\"\"\n    # 实现数据导入逻辑\n    pass\n\nif __name__ == \"__main__\":\n    import_oxford_3000()\n    print(\"单词数据导入完成\")",
        },
        "data": {
            "oxford_3000.csv": "# 牛津3000词表数据\n# 请将实际的CSV文件放在这里",
        },
        "alembic": {
            "versions": {
                "__init__.py": "",
            },
            "env.py": "# 数据库迁移环境配置\nfrom logging.config import fileConfig\n\nfrom sqlalchemy import engine_from_config\nfrom sqlalchemy import pool\n\nfrom alembic import context\n\n# 添加项目根目录到Python路径\nimport sys\nfrom pathlib import Path\nsys.path.append(str(Path(__file__).parent.parent))\n\nfrom app.core.config import settings\nfrom app.models import user, word, relation, contribution  # 导入所有模型\nfrom app.database import SQLModel\n\n# 这是Alembic Config对象，提供对配置值的访问\nconfig = context.config\n\n# 设置数据库URL\nconfig.set_main_option(\"sqlalchemy.url\", settings.database_url)\n\ntarget_metadata = SQLModel.metadata\n\n# 其他配置...",
        },
        "requirements.txt": "fastapi==0.104.1\nuvicorn[standard]==0.24.0\nsqlmodel==0.0.11\npython-multipart==0.0.6\npython-jose[cryptography]==3.3.0\npasslib[bcrypt]==1.7.4\npython-dotenv==1.0.0\nalembic==1.12.1\npandas==2.1.3\npytest==7.4.3\nhttpx==0.25.2",
        ".env": "# 环境变量\nDATABASE_URL=sqlite:///./english_graph.db\nSECRET_KEY=your-secret-key-here-change-in-production",
        ".gitignore": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n\n# VirtualEnv\nvenv/\nenv/\nENV/\n\n# Database\n*.db\n*.sqlite3\n\n# Environment variables\n.env\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n\n# OS\n.DS_Store\nThumbs.db",
        "README.md": "# 英语学习图谱API\n\n基于FastAPI和SQLModel的英语学习图谱后端API。\n\n## 功能特性\n\n- 单词管理\n- 关系图谱\n- 用户系统\n- 贡献审核\n\n## 安装和运行\n\n1. 安装依赖：`pip install -r requirements.txt`\n2. 初始化数据库：`python scripts/init_db.py`\n3. 导入数据：`python scripts/import_words.py`\n4. 启动服务：`uvicorn app.main:app --reload`\n\n## API文档\n\n启动服务后访问：\n- Swagger UI: http://localhost:8000/docs\n- ReDoc: http://localhost:8000/redoc",
    }

    # 创建目录和文件
    def create_structure(base, structure):
        for name, content in structure.items():
            path = base / name
            if isinstance(content, dict):
                # 这是一个目录
                path.mkdir(parents=True, exist_ok=True)
                create_structure(path, content)
            else:
                # 这是一个文件
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

    # 执行创建
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    create_structure(base_path, structure)

    print(f"项目结构已创建在: {base_path.absolute()}")


if __name__ == "__main__":
    project_path = input("请输入项目路径（默认为当前目录）: ").strip()
    if not project_path:
        project_path = "."

    create_project_structure(project_path)