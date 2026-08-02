"""人物、标签、事实、日期、跟进与时间线业务逻辑。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, time

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.models.interaction import Interaction, InteractionParticipant
from app.models.person import FollowUpTask, ImportantDate, Person, PersonFact, PersonTag
from app.models.topic import TopicPersonLink
from app.repositories.person_repository import (
    FollowUpRepository,
    ImportantDateRepository,
    PersonFactRepository,
    PersonRepository,
    TagRepository,
)
from app.schemas.person import (
    FollowUpCreate,
    FollowUpUpdate,
    ImportantDateCreate,
    ImportantDateUpdate,
    PersonCreate,
    PersonFactCreate,
    PersonFactUpdate,
    PersonUpdate,
    TimelineItem,
)


def _as_utc(value: datetime) -> datetime:
    """SQLite 返回 naive 时间，统一补上 UTC 时区。"""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


class PersonService:
    """人物模块服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.persons = PersonRepository(db)
        self.tags = TagRepository(db)
        self.facts = PersonFactRepository(db)
        self.dates = ImportantDateRepository(db)
        self.follow_ups = FollowUpRepository(db)

    # ---- 人物 ----

    def list_persons(
        self, page: int, page_size: int, q: str | None, tag_id: uuid.UUID | None
    ) -> tuple[list[Person], int]:
        stmt = select(Person).options(selectinload(Person.tags)).where(Person.deleted_at.is_(None))
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Person.name.ilike(pattern),
                    Person.nickname.ilike(pattern),
                    Person.organization.ilike(pattern),
                    Person.occupation.ilike(pattern),
                )
            )
        if tag_id:
            stmt = stmt.join(PersonTag, PersonTag.person_id == Person.id).where(
                PersonTag.tag_id == tag_id
            )
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(Person.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_person(self, person_id: uuid.UUID) -> Person:
        stmt = (
            select(Person)
            .options(selectinload(Person.tags))
            .where(Person.id == person_id, Person.deleted_at.is_(None))
        )
        person = self.db.execute(stmt).scalar_one_or_none()
        if person is None:
            raise AppError("NOT_FOUND", status_code=404)
        return person

    def create_person(self, data: PersonCreate) -> Person:
        return self.persons.create(Person(**data.model_dump()))

    def update_person(self, person_id: uuid.UUID, data: PersonUpdate) -> Person:
        values = data.model_dump(exclude_unset=True)
        person = self.persons.update(person_id, values)
        if person is None:
            raise AppError("NOT_FOUND", status_code=404)
        return person

    def delete_person(self, person_id: uuid.UUID) -> None:
        if not self.persons.soft_delete(person_id):
            raise AppError("NOT_FOUND", status_code=404)

    def permanent_delete_person(self, person_id: uuid.UUID, confirm: bool) -> None:
        if not confirm:
            raise AppError("CONFLICT", "需要确认参数 confirm=true", status_code=400)
        person = self.db.get(Person, person_id)
        if person is None:
            raise AppError("NOT_FOUND", status_code=404)
        self.db.execute(delete(PersonTag).where(PersonTag.person_id == person_id))
        self.db.execute(delete(PersonFact).where(PersonFact.person_id == person_id))
        self.db.execute(delete(ImportantDate).where(ImportantDate.person_id == person_id))
        self.db.execute(delete(FollowUpTask).where(FollowUpTask.person_id == person_id))
        self.db.execute(
            delete(InteractionParticipant).where(InteractionParticipant.person_id == person_id)
        )
        self.db.execute(delete(TopicPersonLink).where(TopicPersonLink.person_id == person_id))
        self.db.flush()
        if not self.persons.hard_delete(person_id):
            raise AppError("NOT_FOUND", status_code=404)

    # ---- 标签 ----

    def set_person_tags(self, person_id: uuid.UUID, tag_ids: list[uuid.UUID]) -> Person:
        self.get_person(person_id)
        existing_ids = {
            row.tag_id
            for row in self.db.execute(
                select(PersonTag).where(PersonTag.person_id == person_id)
            ).scalars()
        }
        for tag_id in tag_ids:
            if tag_id not in existing_ids:
                self.db.add(PersonTag(person_id=person_id, tag_id=tag_id))
        for row in self.db.execute(
            select(PersonTag).where(
                PersonTag.person_id == person_id, PersonTag.tag_id.not_in(tag_ids)
            )
        ).scalars():
            self.db.delete(row)
        self.db.flush()
        self.db.expire_all()
        return self.get_person(person_id)

    # ---- 事实 ----

    def list_facts(
        self, person_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[PersonFact], int]:
        self.get_person(person_id)
        stmt = select(PersonFact).where(PersonFact.person_id == person_id)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(PersonFact.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def create_fact(self, person_id: uuid.UUID, data: PersonFactCreate) -> PersonFact:
        self.get_person(person_id)
        return self.facts.create(PersonFact(person_id=person_id, **data.model_dump()))

    def update_fact(self, fact_id: uuid.UUID, data: PersonFactUpdate) -> PersonFact:
        fact = self.facts.update(fact_id, data.model_dump(exclude_unset=True))
        if fact is None:
            raise AppError("NOT_FOUND", status_code=404)
        return fact

    def delete_fact(self, fact_id: uuid.UUID) -> None:
        if not self.facts.hard_delete(fact_id):
            raise AppError("NOT_FOUND", status_code=404)

    # ---- 重要日期 ----

    def list_dates(
        self, person_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[ImportantDate], int]:
        self.get_person(person_id)
        stmt = select(ImportantDate).where(ImportantDate.person_id == person_id)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(ImportantDate.date_value.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def create_date(self, person_id: uuid.UUID, data: ImportantDateCreate) -> ImportantDate:
        self.get_person(person_id)
        return self.dates.create(ImportantDate(person_id=person_id, **data.model_dump()))

    def update_date(self, date_id: uuid.UUID, data: ImportantDateUpdate) -> ImportantDate:
        item = self.dates.update(date_id, data.model_dump(exclude_unset=True))
        if item is None:
            raise AppError("NOT_FOUND", status_code=404)
        return item

    def delete_date(self, date_id: uuid.UUID) -> None:
        if not self.dates.hard_delete(date_id):
            raise AppError("NOT_FOUND", status_code=404)

    # ---- 待跟进 ----

    def list_follow_ups(
        self, person_id: uuid.UUID, page: int, page_size: int, completed: bool | None
    ) -> tuple[list[FollowUpTask], int]:
        self.get_person(person_id)
        stmt = select(self.follow_ups.model).where(
            self.follow_ups.model.person_id == person_id,
            self.follow_ups.model.deleted_at.is_(None),
        )
        if completed is not None:
            stmt = stmt.where(self.follow_ups.model.completed == completed)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(self.follow_ups.model.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def create_follow_up(self, person_id: uuid.UUID, data: FollowUpCreate) -> FollowUpTask:
        self.get_person(person_id)
        return self.follow_ups.create(
            self.follow_ups.model(person_id=person_id, **data.model_dump())
        )

    def update_follow_up(self, task_id: uuid.UUID, data: FollowUpUpdate) -> FollowUpTask:
        task = self.follow_ups.update(task_id, data.model_dump(exclude_unset=True))
        if task is None:
            raise AppError("NOT_FOUND", status_code=404)
        return task

    def delete_follow_up(self, task_id: uuid.UUID) -> None:
        if not self.follow_ups.soft_delete(task_id):
            raise AppError("NOT_FOUND", status_code=404)

    # ---- 时间线 ----

    def get_timeline(
        self, person_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[TimelineItem], int]:
        self.get_person(person_id)
        events: list[TimelineItem] = []

        interactions = self.db.execute(
            select(Interaction)
            .join(
                InteractionParticipant,
                InteractionParticipant.interaction_id == Interaction.id,
            )
            .where(
                InteractionParticipant.person_id == person_id,
                Interaction.deleted_at.is_(None),
            )
        ).scalars()
        for item in interactions:
            events.append(
                TimelineItem(
                    type="interaction",
                    id=item.id,
                    title=item.title,
                    occurred_at=_as_utc(item.occurred_at),
                    summary=item.summary,
                )
            )

        facts = self.db.execute(
            select(PersonFact).where(PersonFact.person_id == person_id)
        ).scalars()
        for fact in facts:
            events.append(
                TimelineItem(
                    type="fact",
                    id=fact.id,
                    title=f"{fact.fact_type}: {fact.content[:40]}",
                    occurred_at=_as_utc(fact.created_at),
                    summary=fact.content,
                )
            )

        dates = self.db.execute(
            select(ImportantDate).where(ImportantDate.person_id == person_id)
        ).scalars()
        for item in dates:
            occurred_at = datetime.combine(item.date_value, time.min, tzinfo=UTC)
            events.append(
                TimelineItem(
                    type="important_date",
                    id=item.id,
                    title=item.title,
                    occurred_at=occurred_at,
                    summary=item.note,
                )
            )

        events.sort(key=lambda e: e.occurred_at, reverse=True)
        total = len(events)
        start = (page - 1) * page_size
        return events[start : start + page_size], total
