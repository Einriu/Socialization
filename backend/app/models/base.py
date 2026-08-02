"""SQLAlchemy 模型基类与通用 Mixin。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


def utcnow() -> datetime:
    """返回当前 UTC 时间。"""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


class UTCDateTime(TypeDecorator):
    """统一以 UTC 存储与读取；SQLite 返回 naive 时自动补充时区。"""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: object, dialect: object) -> object:
        if isinstance(value, datetime) and value.tzinfo is not None:
            return value.astimezone(UTC).replace(tzinfo=None)
        return value

    def process_result_value(self, value: object, dialect: object) -> object:
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class UUIDPrimaryKeyMixin:
    """UUID 主键。"""

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    """创建/更新时间（UTC）。"""

    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )


class SoftDeleteMixin:
    """软删除标记。"""

    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True), nullable=True)
