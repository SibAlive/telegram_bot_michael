"""Устранение ошибок (view)

Revision ID: 0f3847810719
Revises: ce72b912b399
Create Date: 2025-10-09 19:09:33.267708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '0f3847810719'
down_revision: Union[str, Sequence[str], None] = 'ce72b912b399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем старое представление
    op.execute(text("DROP VIEW IF EXISTS points"))

    # Создаём новое представление
    op.execute(text("""
            CREATE VIEW points AS
            SELECT
                f.telegram_id,
                SUM(COALESCE(f.income_points, 0) - COALESCE(f.expense_points, 0)) AS total_points
            FROM finance f
            GROUP BY f.telegram_id
        """))


def downgrade() -> None:
    """Downgrade schema."""
    pass
