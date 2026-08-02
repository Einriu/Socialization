"""支撑表：设置、备份记录、审计日志、Prompt 模板。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UTCDateTime, UUIDPrimaryKeyMixin, utcnow


class AppSetting(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """应用设置键值。"""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[dict | None] = mapped_column(JSON)


class BackupRecord(UUIDPrimaryKeyMixin, Base):
    """备份记录。"""

    __tablename__ = "backup_records"

    filename: Mapped[str] = mapped_column(String(200), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ok")
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )


class AuditLog(Base):
    """审计日志。"""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )


class PromptTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Prompt 模板。"""

    __tablename__ = "prompt_templates"

    template_type: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_editable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
