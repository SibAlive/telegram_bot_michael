"""Таблица points заменена на представление (view)

Revision ID: e06381ce3c0d
Revises: cfec7bfe2fb9
Create Date: 2025-10-09 18:04:11.523359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'e06381ce3c0d'
down_revision: Union[str, Sequence[str], None] = 'cfec7bfe2fb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем старую таблицу
    op.drop_table('points')

    # Создаем представление (view)
    op.execute(text("""
        CREATE VIEW points AS
        SELECT
            f.telegram_id,
            (COALESCE(f.income_points, 0) - COALESCE(f.expense_points, 0) AS total_points
        FROM finance f
    """))


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем таблицу points при откате
    op.create_table(
        'points',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('total_points', sa.Integer(), default=0)
    )
