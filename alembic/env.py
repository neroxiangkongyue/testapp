# 数据库迁移环境配置
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到Python路径
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.models import user, word, relation, contribution  # 导入所有模型
from app.database import SQLModel

# 这是Alembic Config对象，提供对配置值的访问
config = context.config

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = SQLModel.metadata

# 其他配置...