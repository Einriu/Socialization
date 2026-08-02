"""P1 知识库版本：文件、切块、自定义字段、会话摘要、用量与 FTS5。

Revision ID: 0004_p1_tables
Revises: 0003_seed_data
Create Date: 2026-08-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_p1_tables"
down_revision = "0003_seed_data"
branch_labels = None
depends_on = None


def _uuid() -> sa.String:
    return sa.String(32)


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("filename", sa.String(300), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("sha256", sa.String(64), nullable=False, index=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("parse_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "document_versions",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("document_id", _uuid(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "document_chunks",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column(
            "document_id", _uuid(), sa.ForeignKey("documents.id"), nullable=False, index=True
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("heading_path", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "document_links",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column(
            "document_id", _uuid(), sa.ForeignKey("documents.id"), nullable=False, index=True
        ),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), nullable=True),
        sa.Column("topic_id", _uuid(), sa.ForeignKey("topics.id"), nullable=True),
        sa.Column("conversation_id", _uuid(), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "processing_jobs",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column(
            "document_id", _uuid(), sa.ForeignKey("documents.id"), nullable=False, index=True
        ),
        sa.Column("job_type", sa.String(30), nullable=False, server_default="parse"),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_table(
        "custom_fields",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("field_type", sa.String(30), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("group_name", sa.String(50), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "custom_field_values",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("custom_field_id", _uuid(), sa.ForeignKey("custom_fields.id"), nullable=False),
        sa.Column("person_id", _uuid(), sa.ForeignKey("persons.id"), nullable=False, index=True),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("custom_field_id", "person_id", name="uq_custom_field_value"),
    )
    op.create_table(
        "conversation_summaries",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column(
            "conversation_id",
            _uuid(),
            sa.ForeignKey("conversations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "context_snapshots",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column(
            "conversation_id",
            _uuid(),
            sa.ForeignKey("conversations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("message_id", _uuid(), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "ai_usage_logs",
        sa.Column("id", _uuid(), primary_key=True),
        sa.Column("provider_id", _uuid(), nullable=True),
        sa.Column("model_id", _uuid(), nullable=True),
        sa.Column("conversation_id", _uuid(), nullable=True),
        sa.Column("token_input", sa.Integer(), nullable=True),
        sa.Column("token_output", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # FTS5 全文索引（SQLite 内置支持）
    op.execute(
        "CREATE VIRTUAL TABLE fts_documents USING fts5("
        "content, document_id UNINDEXED, chunk_index UNINDEXED, id UNINDEXED)"
    )
    op.execute(
        "CREATE VIRTUAL TABLE fts_notes USING fts5("
        "plain_text, topic_id UNINDEXED, id UNINDEXED)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS fts_notes")
    op.execute("DROP TABLE IF EXISTS fts_documents")
    tables = [
        "ai_usage_logs",
        "context_snapshots",
        "conversation_summaries",
        "custom_field_values",
        "custom_fields",
        "processing_jobs",
        "document_links",
        "document_chunks",
        "document_versions",
        "documents",
    ]
    for table in tables:
        op.drop_table(table)
