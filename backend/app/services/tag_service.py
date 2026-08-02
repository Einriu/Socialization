"""标签业务逻辑。"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.person import PersonTag, Tag
from app.repositories.person_repository import TagRepository
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    """标签服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.tags = TagRepository(db)

    def list_tags(self) -> tuple[list[Tag], int]:
        stmt = select(Tag).order_by(Tag.created_at.asc())
        rows = self.db.execute(stmt).scalars().all()
        return list(rows), len(rows)

    def create_tag(self, data: TagCreate) -> Tag:
        name = data.name.strip()
        exists = self.db.execute(select(Tag).where(Tag.name == name)).scalar_one_or_none()
        if exists is not None:
            raise AppError("CONFLICT", f"标签已存在：{name}", status_code=409)
        payload = data.model_dump(exclude_unset=True)
        payload["name"] = name
        return self.tags.create(Tag(**payload))

    def update_tag(self, tag_id: uuid.UUID, data: TagUpdate) -> Tag:
        values = data.model_dump(exclude_unset=True)
        if "name" in values:
            name = values["name"].strip()
            dup = self.db.execute(
                select(Tag).where(Tag.name == name, Tag.id != tag_id)
            ).scalar_one_or_none()
            if dup is not None:
                raise AppError("CONFLICT", f"标签已存在：{name}", status_code=409)
            values["name"] = name
        tag = self.tags.update(tag_id, values)
        if tag is None:
            raise AppError("NOT_FOUND", status_code=404)
        return tag

    def delete_tag(self, tag_id: uuid.UUID) -> None:
        tag = self.db.get(Tag, tag_id)
        if tag is None:
            raise AppError("NOT_FOUND", status_code=404)
        for link in self.db.execute(
            select(PersonTag).where(PersonTag.tag_id == tag_id)
        ).scalars():
            self.db.delete(link)
        self.db.flush()
        if not self.tags.hard_delete(tag_id):
            raise AppError("NOT_FOUND", status_code=404)

    def count_usages(self, tag_id: uuid.UUID) -> int:
        return int(
            self.db.execute(
                select(func.count()).select_from(PersonTag).where(PersonTag.tag_id == tag_id)
            ).scalar_one()
        )
