"""AI 提供商、模型与会话模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UTCDateTime, UUIDPrimaryKeyMixin


class AIProvider(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """AI 提供商配置。"""

    __tablename__ = "ai_providers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="openai_compatible"
    )
    base_url: Mapped[str | None] = mapped_column(Text)
    encrypted_api_key: Mapped[str | None] = mapped_column(Text)
    custom_headers: Mapped[dict | None] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    proxy: Mapped[str | None] = mapped_column(Text)
    default_model_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    last_tested_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True))

    models: Mapped[list[AIModel]] = relationship(
        back_populates="provider", cascade="all, delete-orphan"
    )


class AIModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """模型（同步或手动添加）。"""

    __tablename__ = "ai_models"

    provider_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("ai_providers.id"), nullable=False, index=True
    )
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    model_type: Mapped[str] = mapped_column(String(30), nullable=False, default="chat")
    context_length: Mapped[int | None] = mapped_column(Integer)
    supports_streaming: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    supports_tools: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supports_json: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supports_vision: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supports_reasoning: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    input_price_note: Mapped[str | None] = mapped_column(String(200))
    output_price_note: Mapped[str | None] = mapped_column(String(200))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")

    provider: Mapped[AIProvider] = relationship(back_populates="models")


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """AI 会话。"""

    __tablename__ = "conversations"

    title: Mapped[str] = mapped_column(String(200), nullable=False, default="新对话")
    mode: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    provider_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("ai_providers.id"))
    model_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("ai_models.id"))
    summary: Mapped[str | None] = mapped_column(Text)
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    messages: Mapped[list[ConversationMessage]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    links: Mapped[list[ConversationLink]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class ConversationMessage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """会话消息。"""

    __tablename__ = "conversation_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("conversations.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    reasoning_content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    token_input: Mapped[int | None] = mapped_column(Integer)
    token_output: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    provider_message_id: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class ConversationLink(Base):
    """会话关联（人物/话题/文件）。"""

    __tablename__ = "conversation_links"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("conversations.id"), nullable=False, index=True
    )
    person_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    # document_id 在 P1 引入 documents 表后改为正式外键
    document_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)

    conversation: Mapped[Conversation] = relationship(back_populates="links")
