"""自定义字段定义与人物取值业务逻辑。"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.p1 import CustomField, CustomFieldValue
from app.models.person import Person
from app.repositories.base import BaseRepository
from app.schemas.p1 import CustomFieldCreate, CustomFieldUpdate


class CustomFieldRepository(BaseRepository[CustomField]):
    model = CustomField


class CustomFieldService:
    """自定义字段服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.fields = CustomFieldRepository(db)

    def list_fields(self) -> list[CustomField]:
        return list(
            self.db.execute(
                select(CustomField)
                .where(CustomField.deleted_at.is_(None))
                .order_by(CustomField.sort_order.asc(), CustomField.created_at.asc())
            ).scalars()
        )

    def create_field(self, data: CustomFieldCreate) -> CustomField:
        return self.fields.create(CustomField(**data.model_dump()))

    def update_field(
        self, field_id: uuid.UUID, data: CustomFieldUpdate
    ) -> CustomField:
        field = self.fields.update(field_id, data.model_dump(exclude_unset=True))
        if field is None:
            raise AppError("NOT_FOUND", status_code=404)
        return field

    def delete_field(self, field_id: uuid.UUID) -> None:
        if not self.fields.soft_delete(field_id):
            raise AppError("NOT_FOUND", status_code=404)

    def get_values(self, person_id: uuid.UUID) -> dict[str, object]:
        if self.db.get(Person, person_id) is None:
            raise AppError("NOT_FOUND", status_code=404)
        rows = self.db.execute(
            select(CustomFieldValue).where(CustomFieldValue.person_id == person_id)
        ).scalars()
        return {str(row.custom_field_id): row.value for row in rows}

    def set_values(
        self, person_id: uuid.UUID, values: dict[uuid.UUID, object]
    ) -> dict[str, object]:
        if self.db.get(Person, person_id) is None:
            raise AppError("NOT_FOUND", status_code=404)
        existing = {
            row.custom_field_id: row
            for row in self.db.execute(
                select(CustomFieldValue).where(CustomFieldValue.person_id == person_id)
            ).scalars()
        }
        for field_id, value in values.items():
            if self.db.get(CustomField, field_id) is None:
                raise AppError("NOT_FOUND", f"字段不存在：{field_id}", status_code=404)
            row = existing.get(field_id)
            if row is None:
                self.db.add(
                    CustomFieldValue(
                        custom_field_id=field_id, person_id=person_id, value=value
                    )
                )
            else:
                row.value = value
        self.db.flush()
        return self.get_values(person_id)
