"""空基线迁移。

建立 alembic_version 表，为 M1 里程碑追加业务表迁移预留起点。

Revision ID: 0001_empty_initial
Revises:
Create Date: 2026-08-02
"""

# revision identifiers, used by Alembic.
revision = "0001_empty_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """M1 将在此之后追加业务表；当前仅建立迁移基线。"""
    pass


def downgrade() -> None:
    pass
