"""add bravata to scenes

Revision ID: 992820b2e5c3
Revises: 78c1ea172f01
Create Date: 2026-06-03 19:44:08.760014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '992820b2e5c3'
down_revision: Union[str, Sequence[str], None] = '78c1ea172f01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('scenes', sa.Column('bravata', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('scenes', 'bravata')
