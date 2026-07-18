"""bridge revision for existing database stamp

Revision ID: 71486b3bf5e8
Revises: 8f4c3deebaa2
Create Date: 2026-07-13

"""
#pylint: skip-file
from typing import Sequence, Union

from alembic import op


revision: str = "71486b3bf5e8"
down_revision: Union[str, Sequence[str], None] = "8f4c3deebaa2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass