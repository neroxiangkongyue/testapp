# alembic/versions/xxxx_add_description_to_wordrelation.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 添加 description 列
    op.add_column('wordrelation', sa.Column('description', sa.String(), nullable=True))

def downgrade():
    # 移除 description 列
    op.drop_column('wordrelation', 'description')