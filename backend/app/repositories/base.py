"""通用 Repository 基座：分页、软删除、审计。"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import Base, utcnow
from app.models.support import AuditLog


class BaseRepository[ModelT: Base]:
    """提供 get/list/create/update/soft_delete/hard_delete 与审计写入。"""

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def _active_filter(self, stmt: object) -> object:
        if hasattr(self.model, "deleted_at"):
            return stmt.where(self.model.deleted_at.is_(None))  # type: ignore[attr-defined]
        return stmt

    def _write_audit(self, entity: ModelT, action: str, summary: str | None = None) -> None:
        self.db.add(
            AuditLog(
                entity_type=self.model.__tablename__,
                entity_id=str(entity.id),
                action=action,
                summary=summary,
            )
        )

    def get(self, entity_id: uuid.UUID) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == entity_id)
        result = self.db.execute(self._active_filter(stmt))  # type: ignore[arg-type]
        return result.scalar_one_or_none()

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[ModelT], int]:
        base = self._active_filter(select(self.model))  # type: ignore[arg-type]
        total_stmt = select(func.count()).select_from(base.subquery())
        total = self.db.execute(total_stmt).scalar_one()
        rows = (
            self.db.execute(
                base.order_by(self.model.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def create(self, entity: ModelT) -> ModelT:
        self.db.add(entity)
        self.db.flush()
        self._write_audit(entity, "create")
        return entity

    def update(self, entity_id: uuid.UUID, values: dict[str, object]) -> ModelT | None:
        entity = self.get(entity_id)
        if entity is None:
            return None
        for key, value in values.items():
            setattr(entity, key, value)
        self.db.flush()
        self._write_audit(entity, "update")
        return entity

    def soft_delete(self, entity_id: uuid.UUID) -> bool:
        entity = self.get(entity_id)
        if entity is None or not hasattr(entity, "deleted_at"):
            return False
        entity.deleted_at = utcnow()
        self.db.flush()
        self._write_audit(entity, "delete")
        return True

    def hard_delete(self, entity_id: uuid.UUID) -> bool:
        entity = self.db.get(self.model, entity_id)
        if entity is None:
            return False
        self.db.delete(entity)
        self.db.flush()
        self._write_audit(entity, "hard_delete")
        return True
