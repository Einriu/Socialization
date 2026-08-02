"""创建 P0 全部业务表。

Revision ID: 0002_p0_tables
Revises: 0001_empty_initial
Create Date: 2026-08-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_p0_tables"
down_revision = "0001_empty_initial"
branch_labels = None
depends_on = None


def _uuid() -> sa.String:
    """UUID 在 SQLite 中以 32 位十六进制字符串存储。"""
    return sa.String(32)


def upgrade() -> None:
    op.create_table(
        "topic_categories",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("parent_id", _uuid(), sa.ForeignKey("topic_categories.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "persons",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("nickname", sa.String(100), nullable=True),
        sa.Column("avatar_path", sa.Text(), nullable=True),
        sa.Column("relationship_type", sa.String(50), nullable=True),
        sa.Column("familiarity_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("met_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("met_location", sa.Text(), nullable=True),
        sa.Column("met_via", sa.Text(), nullable=True),
        sa.Column("organization", sa.String(200), nullable=True),
        sa.Column("occupation", sa.String(100), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("privacy_level", sa.String(20), nullable=False, server_default="private"),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_persons_name", "persons", ["name"])
    op.create_table(
        "tags",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("group_name", sa.String(50), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tags_name", "tags", ["name"], unique=True)
    op.create_table(
        "person_tags",
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), primary_key=True),
        sa.Column("tag_id", _uuid(), sa.ForeignKey("tags.id"), primary_key=True),
        sa.UniqueConstraint("person_id", "tag_id", name="uq_person_tags"),
    )
    op.create_table(
        "person_facts",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), nullable=False),
        sa.Column("fact_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False, server_default="user"),
        sa.Column("source_id", _uuid(), nullable=True),
        sa.Column("confidence", sa.String(20), nullable=False, server_default="confirmed"),
        sa.Column("is_sensitive", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_person_facts_person_id", "person_facts", ["person_id"])
    op.create_table(
        "important_dates",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("kind", sa.String(30), nullable=True),
        sa.Column("date_value", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_important_dates_person_id", "important_dates", ["person_id"])
    op.create_table(
        "topics",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category_id", _uuid(), sa.ForeignKey("topic_categories.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mastery_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_topics_name", "topics", ["name"])
    op.create_table(
        "topic_notes",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("topic_id", _uuid(), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=True),
        sa.Column("plain_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_topic_notes_topic_id", "topic_notes", ["topic_id"], unique=True)
    op.create_table(
        "topic_person_links",
        sa.Column("topic_id", _uuid(), sa.ForeignKey("topics.id"), primary_key=True),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), primary_key=True),
        sa.UniqueConstraint("topic_id", "person_id", name="uq_topic_person_links"),
    )
    op.create_table(
        "interactions",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("interaction_type", sa.String(30), nullable=False, server_default="face_to_face"),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("new_info", sa.Text(), nullable=True),
        sa.Column("mood_state", sa.Text(), nullable=True),
        sa.Column("my_performance", sa.Text(), nullable=True),
        sa.Column("positive_feedback", sa.Text(), nullable=True),
        sa.Column("awkward_points", sa.Text(), nullable=True),
        sa.Column("follow_up", sa.Text(), nullable=True),
        sa.Column("privacy_level", sa.String(20), nullable=False, server_default="private"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_interactions_occurred_at", "interactions", ["occurred_at"])
    op.create_table(
        "interaction_participants",
        sa.Column("interaction_id", _uuid(), sa.ForeignKey("interactions.id"), primary_key=True),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), primary_key=True),
        sa.UniqueConstraint(
            "interaction_id", "person_id", name="uq_interaction_participants"
        ),
    )
    op.create_table(
        "interaction_topics",
        sa.Column("interaction_id", _uuid(), sa.ForeignKey("interactions.id"), primary_key=True),
        sa.Column("topic_id", _uuid(), sa.ForeignKey("topics.id"), primary_key=True),
        sa.UniqueConstraint("interaction_id", "topic_id", name="uq_interaction_topics"),
    )
    op.create_table(
        "follow_up_tasks",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), nullable=True),
        sa.Column("interaction_id", _uuid(), sa.ForeignKey("interactions.id"), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_follow_up_tasks_person_id", "follow_up_tasks", ["person_id"])
    op.create_table(
        "ai_providers",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "provider_type",
            sa.String(30),
            nullable=False,
            server_default="openai_compatible",
        ),
        sa.Column("base_url", sa.Text(), nullable=True),
        sa.Column("encrypted_api_key", sa.Text(), nullable=True),
        sa.Column("custom_headers", sa.JSON(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("proxy", sa.Text(), nullable=True),
        sa.Column("default_model_id", _uuid(), nullable=True),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "ai_models",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("provider_id", _uuid(), sa.ForeignKey("ai_providers.id"), nullable=False),
        sa.Column("model_id", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("model_type", sa.String(30), nullable=False, server_default="chat"),
        sa.Column("context_length", sa.Integer(), nullable=True),
        sa.Column("supports_streaming", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("supports_tools", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("supports_json", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("supports_vision", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("supports_reasoning", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("input_price_note", sa.String(200), nullable=True),
        sa.Column("output_price_note", sa.String(200), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_models_provider_id", "ai_models", ["provider_id"])
    op.create_table(
        "conversations",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False, server_default="新对话"),
        sa.Column("mode", sa.String(50), nullable=False, server_default="general"),
        sa.Column("provider_id", _uuid(), sa.ForeignKey("ai_providers.id"), nullable=True),
        sa.Column("model_id", _uuid(), sa.ForeignKey("ai_models.id"), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "conversation_messages",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("conversation_id", _uuid(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("reasoning_content", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="completed"),
        sa.Column("token_input", sa.Integer(), nullable=True),
        sa.Column("token_output", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("provider_message_id", sa.String(100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("generated_by_ai", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_conversation_messages_conversation_id", "conversation_messages", ["conversation_id"]
    )
    op.create_table(
        "conversation_links",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("conversation_id", _uuid(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("person_id", _uuid(), nullable=True),
        sa.Column("topic_id", _uuid(), nullable=True),
        sa.Column("document_id", _uuid(), nullable=True),
    )
    op.create_index(
        "ix_conversation_links_conversation_id", "conversation_links", ["conversation_id"]
    )
    op.create_table(
        "app_settings",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_app_settings_key", "app_settings", ["key"], unique=True)
    op.create_table(
        "backup_records",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("filename", sa.String(200), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_table(
        "prompt_templates",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("template_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_editable", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_prompt_templates_template_type",
        "prompt_templates",
        ["template_type"],
        unique=True,
    )


def downgrade() -> None:
    tables = [
        "prompt_templates",
        "audit_logs",
        "backup_records",
        "app_settings",
        "conversation_links",
        "conversation_messages",
        "conversations",
        "ai_models",
        "ai_providers",
        "follow_up_tasks",
        "interaction_topics",
        "interaction_participants",
        "interactions",
        "topic_person_links",
        "topic_notes",
        "topics",
        "important_dates",
        "person_facts",
        "person_tags",
        "tags",
        "persons",
        "topic_categories",
    ]
    for table in tables:
        op.drop_table(table)
