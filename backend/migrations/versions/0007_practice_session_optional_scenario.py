"""练习会话支持无预设场景：scenario_id 可空（自定义背景直建会话）。

Revision ID: 0007
Revises: 0006_practice_custom
Create Date: 2026-08-03
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007_practice_session_optional_scenario"
down_revision = "0006_practice_custom"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """允许 practice_sessions.scenario_id 为空。"""
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.alter_column(
            "scenario_id", existing_type=sa.Uuid(), nullable=True
        )


def downgrade() -> None:
    """恢复非空约束（存在空值时可能失败，属预期）。"""
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.alter_column(
            "scenario_id", existing_type=sa.Uuid(), nullable=False
        )
