"""P2 社交能力版本：提取确认、复习、练习、记忆、目标、关系。

Revision ID: 0005_p2_tables
Revises: 0004_p1_tables
Create Date: 2026-08-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_p2_tables"
down_revision = "0004_p1_tables"
branch_labels = None
depends_on = None


def _uuid() -> sa.String:
    return sa.String(32)


PRACTICE_SCENARIOS = [
    ("stranger", "陌生人初次交流", "第一次见面，如何自然地开启对话并找到共同话题。"),
    ("colleague", "同事闲聊", "与同事在茶水间/午休时间轻松闲聊。"),
    ("dinner", "饭局交流", "多人饭局中得体地加入话题并照顾他人。"),
    ("party", "聚会加入话题", "在聚会上加入正在进行的对话。"),
    ("friend", "朋友近况交流", "与朋友聊近况，表达关心而不越界。"),
    ("introvert", "与内向者聊天", "对方比较内向，需要放慢节奏、多倾听。"),
    ("talker", "与健谈者聊天", "对方很健谈，如何自然地承接而不被带偏。"),
    ("boss", "与上级交流", "与上级进行非正式交流，保持尊重与自然。"),
    ("awkward", "冷场恢复", "对话出现冷场时如何自然救场。"),
    ("disagreement", "观点不同交流", "与观点不同的人交流，求同存异。"),
    ("refuse", "拒绝他人", "得体地拒绝不合理的请求。"),
    ("boundary", "表达边界", "温和而坚定地表达自己的边界。"),
    ("gratitude", "表达感谢或关心", "真诚地表达感谢或对他人处境的关心。"),
]


def upgrade() -> None:
    op.create_table(
        "interaction_extracted_facts",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("interaction_id", _uuid(), sa.ForeignKey("interactions.id"), nullable=False),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), nullable=True),
        sa.Column("kind", sa.String(20), nullable=False, server_default="fact"),
        sa.Column("fact_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "topic_learning_records",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("topic_id", _uuid(), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("learned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mastery_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "review_tasks",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("topic_id", _uuid(), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "practice_scenarios",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("scenario_type", sa.String(30), nullable=False, unique=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("role_params", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "practice_sessions",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("scenario_id", _uuid(), sa.ForeignKey("practice_scenarios.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "practice_messages",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("session_id", _uuid(), sa.ForeignKey("practice_sessions.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "practice_evaluations",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("session_id", _uuid(), sa.ForeignKey("practice_sessions.id"), nullable=False),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "memory_items",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("kind", sa.String(30), nullable=False, server_default="preference"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="proposed"),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "user_profiles",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("expression_preferences", sa.JSON(), nullable=True),
        sa.Column("social_goals", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "person_relationships",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("person_a_id", _uuid(), sa.ForeignKey("persons.id"), nullable=False),
        sa.Column("person_b_id", _uuid(), sa.ForeignKey("persons.id"), nullable=False),
        sa.Column("relation_type", sa.String(50), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    from datetime import UTC, datetime

    now = datetime.now(UTC)
    scenarios = sa.table(
        "practice_scenarios",
        sa.column("id", sa.String),
        sa.column("scenario_type", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("role_params", sa.JSON),
        sa.column("created_at", sa.DateTime),
    )
    import uuid

    op.bulk_insert(
        scenarios,
        [
            {
                "id": uuid.uuid4().hex,
                "scenario_type": scenario_type,
                "title": title,
                "description": description,
                "role_params": {"scenario": title},
                "created_at": now,
            }
            for scenario_type, title, description in PRACTICE_SCENARIOS
        ],
    )


def downgrade() -> None:
    tables = [
        "person_relationships",
        "user_profiles",
        "memory_items",
        "practice_evaluations",
        "practice_messages",
        "practice_sessions",
        "practice_scenarios",
        "review_tasks",
        "topic_learning_records",
        "interaction_extracted_facts",
    ]
    for table in tables:
        op.drop_table(table)
