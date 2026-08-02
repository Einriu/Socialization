"""话题、分类与笔记业务逻辑。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.models.topic import Topic, TopicCategory, TopicNote, TopicPersonLink
from app.repositories.base import BaseRepository
from app.schemas.topic import (
    NoteSave,
    TopicCategoryCreate,
    TopicCategoryUpdate,
    TopicCreate,
    TopicPersonsUpdate,
    TopicUpdate,
)


class TopicRepository(BaseRepository[Topic]):
    model = Topic


class CategoryRepository(BaseRepository[TopicCategory]):
    model = TopicCategory


class NoteRepository(BaseRepository[TopicNote]):
    model = TopicNote


class TopicService:
    """话题模块服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.topics = TopicRepository(db)
        self.categories = CategoryRepository(db)
        self.notes = NoteRepository(db)

    # ---- 分类 ----

    def list_categories(self) -> list[TopicCategory]:
        rows = self.db.execute(
            select(TopicCategory).order_by(TopicCategory.created_at.asc())
        ).scalars()
        return list(rows)

    def category_tree(self) -> list[dict]:
        """返回分类树根节点列表。"""
        nodes: dict[uuid.UUID, dict] = {}
        for row in self.list_categories():
            nodes[row.id] = {
                "id": row.id,
                "name": row.name,
                "parent_id": row.parent_id,
                "created_at": row.created_at,
                "children": [],
            }
        roots: list[dict] = []
        for node in nodes.values():
            parent = node["parent_id"]
            if parent is not None and parent in nodes:
                nodes[parent]["children"].append(node)
            else:
                roots.append(node)
        return roots

    def create_category(self, data: TopicCategoryCreate) -> TopicCategory:
        if data.parent_id is not None and self.db.get(TopicCategory, data.parent_id) is None:
            raise AppError("NOT_FOUND", "父分类不存在", status_code=404)
        return self.categories.create(
            TopicCategory(name=data.name.strip(), parent_id=data.parent_id)
        )

    def update_category(
        self, category_id: uuid.UUID, data: TopicCategoryUpdate
    ) -> TopicCategory:
        values = data.model_dump(exclude_unset=True)
        if data.parent_id is not None:
            if data.parent_id == category_id:
                raise AppError("CONFLICT", "分类不能作为自己的父级", status_code=409)
            if self.db.get(TopicCategory, data.parent_id) is None:
                raise AppError("NOT_FOUND", "父分类不存在", status_code=404)
            ancestor: TopicCategory | None = self.db.get(TopicCategory, data.parent_id)
            while ancestor is not None:
                if ancestor.parent_id == category_id:
                    raise AppError("CONFLICT", "不能形成循环层级", status_code=409)
                ancestor = (
                    self.db.get(TopicCategory, ancestor.parent_id)
                    if ancestor.parent_id is not None
                    else None
                )
        if "name" in values:
            values["name"] = str(values["name"]).strip()
        category = self.categories.update(category_id, values)
        if category is None:
            raise AppError("NOT_FOUND", status_code=404)
        return category

    def delete_category(self, category_id: uuid.UUID) -> None:
        children = self.db.execute(
            select(TopicCategory).where(TopicCategory.parent_id == category_id)
        ).scalars()
        if len(list(children)) > 0:
            raise AppError("CONFLICT", "请先删除子分类", status_code=409)
        used = self.db.execute(
            select(Topic).where(
                Topic.category_id == category_id, Topic.deleted_at.is_(None)
            )
        ).scalar_one_or_none()
        if used is not None:
            raise AppError("CONFLICT", "分类下仍有话题", status_code=409)
        if not self.categories.hard_delete(category_id):
            raise AppError("NOT_FOUND", status_code=404)

    # ---- 话题 ----

    def list_topics(
        self, page: int, page_size: int, q: str | None, category_id: uuid.UUID | None
    ) -> tuple[list[Topic], int]:
        stmt = select(Topic).options(selectinload(Topic.persons)).where(Topic.deleted_at.is_(None))
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(or_(Topic.name.ilike(pattern), Topic.description.ilike(pattern)))
        if category_id:
            stmt = stmt.where(Topic.category_id == category_id)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(Topic.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_topic(self, topic_id: uuid.UUID) -> Topic:
        stmt = (
            select(Topic)
            .options(selectinload(Topic.persons))
            .where(Topic.id == topic_id, Topic.deleted_at.is_(None))
        )
        topic = self.db.execute(stmt).scalar_one_or_none()
        if topic is None:
            raise AppError("NOT_FOUND", status_code=404)
        return topic

    def create_topic(self, data: TopicCreate) -> Topic:
        if data.category_id is not None and self.db.get(TopicCategory, data.category_id) is None:
            raise AppError("NOT_FOUND", "分类不存在", status_code=404)
        return self.topics.create(Topic(**data.model_dump()))

    def update_topic(self, topic_id: uuid.UUID, data: TopicUpdate) -> Topic:
        values = data.model_dump(exclude_unset=True)
        if data.category_id is not None and self.db.get(TopicCategory, data.category_id) is None:
            raise AppError("NOT_FOUND", "分类不存在", status_code=404)
        topic = self.topics.update(topic_id, values)
        if topic is None:
            raise AppError("NOT_FOUND", status_code=404)
        return topic

    def delete_topic(self, topic_id: uuid.UUID) -> None:
        if not self.topics.soft_delete(topic_id):
            raise AppError("NOT_FOUND", status_code=404)

    def set_topic_persons(
        self, topic_id: uuid.UUID, data: TopicPersonsUpdate
    ) -> Topic:
        self.get_topic(topic_id)
        existing_ids = {
            row.person_id
            for row in self.db.execute(
                select(TopicPersonLink).where(TopicPersonLink.topic_id == topic_id)
            ).scalars()
        }
        for person_id in data.person_ids:
            if person_id not in existing_ids:
                self.db.add(TopicPersonLink(topic_id=topic_id, person_id=person_id))
        for row in self.db.execute(
            select(TopicPersonLink).where(
                TopicPersonLink.topic_id == topic_id,
                TopicPersonLink.person_id.not_in(data.person_ids),
            )
        ).scalars():
            self.db.delete(row)
        self.db.flush()
        self.db.expire_all()
        return self.get_topic(topic_id)

    # ---- 笔记 ----

    def get_note(self, topic_id: uuid.UUID) -> TopicNote | None:
        self.get_topic(topic_id)
        return self.db.execute(
            select(TopicNote).where(TopicNote.topic_id == topic_id)
        ).scalar_one_or_none()

    def save_note(self, topic_id: uuid.UUID, data: NoteSave) -> TopicNote:
        self.get_topic(topic_id)
        note = self.get_note(topic_id)
        if note is not None and data.expected_updated_at:
            expected = _parse_utc(data.expected_updated_at)
            actual = note.updated_at
            if actual.tzinfo is None:
                actual = actual.replace(tzinfo=UTC)
            if expected is not None and actual != expected:
                raise AppError(
                    "CONFLICT", "笔记已被其他编辑修改，请刷新后重试", status_code=409
                )
        if note is None:
            note = TopicNote(
                topic_id=topic_id,
                content_json=data.content_json,
                plain_text=data.plain_text,
            )
            self.db.add(note)
        else:
            note.content_json = data.content_json
            note.plain_text = data.plain_text
        self.db.flush()
        return note


def _parse_utc(value: str) -> datetime | None:
    """解析可能带偏移或 Z 后缀的时间字符串为 UTC。"""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
