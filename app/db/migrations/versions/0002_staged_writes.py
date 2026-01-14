"""staged writes table

Revision ID: 0002_staged_writes
Revises: 0001_initial
Create Date: 2026-01-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_staged_writes"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "staged_writes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("validation_summary", postgresql.JSONB(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("committed_node_id", sa.String(length=36), nullable=True),
        sa.Column("committed_at", sa.DateTime(), nullable=True),
        sa.Column("receipt", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("staged_writes")
