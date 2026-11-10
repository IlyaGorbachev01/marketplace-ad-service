"""add outbox trace id

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "outbox",
        sa.Column("trace_id", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("outbox", "trace_id")
