"""P3 练习自定义：渠道、标签、自定义提示词与多人配置。

Revision ID: 0006_practice_custom
Revises: 0005_p2_tables
Create Date: 2026-08-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006_practice_custom"
down_revision = "0005_p2_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "practice_scenarios",
        sa.Column("channel", sa.String(10), nullable=False, server_default="offline"),
    )
    op.add_column("practice_scenarios", sa.Column("tags", sa.JSON(), nullable=True))
    op.add_column("practice_scenarios", sa.Column("custom_prompt", sa.Text(), nullable=True))
    op.add_column("practice_scenarios", sa.Column("participants", sa.JSON(), nullable=True))
    op.add_column(
        "practice_sessions",
        sa.Column("channel", sa.String(10), nullable=False, server_default="offline"),
    )
    op.add_column("practice_sessions", sa.Column("tags", sa.JSON(), nullable=True))
    op.add_column("practice_sessions", sa.Column("custom_prompt", sa.Text(), nullable=True))
    op.add_column("practice_sessions", sa.Column("participants", sa.JSON(), nullable=True))


def downgrade() -> None:
    for column in ("participants", "custom_prompt", "tags", "channel"):
        op.drop_column("practice_sessions", column)
        op.drop_column("practice_scenarios", column)
