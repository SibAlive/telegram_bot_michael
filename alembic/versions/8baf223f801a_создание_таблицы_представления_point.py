"""Создание таблицы представления Point

Revision ID: 8baf223f801a
Revises: 223706a2f5ce
Create Date: 2025-12-04 14:49:31.650211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8baf223f801a'
down_revision: Union[str, Sequence[str], None] = '223706a2f5ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE OR REPLACE VIEW points AS
        SELECT 
            f.telegram_id,
            COALESCE(SUM(f.income_points - f.expense_points), 0) as total_points
        FROM finance f
        GROUP BY f.telegram_id;
    """)


def downgrade():
    op.execute("DROP VIEW IF EXISTS points;")