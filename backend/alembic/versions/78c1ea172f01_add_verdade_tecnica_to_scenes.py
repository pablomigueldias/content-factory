"""add verdade_tecnica to scenes

Revision ID: 78c1ea172f01
Revises: 1c4c707ddebb
Create Date: 2026-06-03 19:35:21.413061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78c1ea172f01'
down_revision: Union[str, Sequence[str], None] = '1c4c707ddebb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('scenes', sa.Column('verdade_tecnica', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('scenes', 'verdade_tecnica')
