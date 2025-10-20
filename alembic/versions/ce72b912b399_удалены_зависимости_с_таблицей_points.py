"""Удалены зависимости с таблицей points

Revision ID: ce72b912b399
Revises: e06381ce3c0d
Create Date: 2025-10-09 18:44:18.177608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce72b912b399'
down_revision: Union[str, Sequence[str], None] = 'e06381ce3c0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
