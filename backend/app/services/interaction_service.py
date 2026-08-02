"""互动记录业务逻辑。"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.models.interaction import Interaction, InteractionParticipant, InteractionTopic
from app.models.person import FollowUpTask, Person
from app.models.topic import Topic
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.interaction import InteractionCreate, InteractionUpdate


class InteractionService:
    """互动服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.interactions = InteractionRepository(db)

    def _load(self, interaction_id: uuid.UUID) -> Interaction:
        stmt = (
            select(Interaction)
            .options(
                selectinload(Interaction.persons),
                selectinload(Interaction.topics),
            )
            .where(Interaction.id == interaction_id, Interaction.deleted_at.is_(None))
        )
        interaction = self.db.execute(stmt).scalar_one_or_none()
        if interaction is None:
            raise AppError("NOT_FOUND", status_code=404)
        return interaction

    def _validate_links(
        self, participant_ids: list[uuid.UUID], topic_ids: list[uuid.UUID]
    ) -> None:
        if participant_ids:
            found = set(
                self.db.execute(
                    select(Person.id).where(Person.id.in_(participant_ids))
                ).scalars()
            )
            missing = set(participant_ids) - found
            if missing:
                raise AppError("NOT_FOUND", "部分关联人物不存在", status_code=404)
        if topic_ids:
            found = set(
                self.db.execute(select(Topic.id).where(Topic.id.in_(topic_ids))).scalars()
            )
            missing = set(topic_ids) - found
            if missing:
                raise AppError("NOT_FOUND", "部分关联话题不存在", status_code=404)

    def list_interactions(
        self,
        page: int,
        page_size: int,
        person_id: uuid.UUID | None,
        topic_id: uuid.UUID | None,
        start: str | None,
        end: str | None,
    ) -> tuple[list[Interaction], int]:
        stmt = select(Interaction).options(
            selectinload(Interaction.persons), selectinload(Interaction.topics)
        ).where(Interaction.deleted_at.is_(None))
        if person_id is not None:
            stmt = stmt.join(
                InteractionParticipant,
                InteractionParticipant.interaction_id == Interaction.id,
            ).where(InteractionParticipant.person_id == person_id)
        if topic_id is not None:
            stmt = stmt.join(
                InteractionTopic,
                InteractionTopic.interaction_id == Interaction.id,
            ).where(InteractionTopic.topic_id == topic_id)
        if start:
            stmt = stmt.where(Interaction.occurred_at >= start)
        if end:
            stmt = stmt.where(Interaction.occurred_at <= end)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(Interaction.occurred_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_interaction(self, interaction_id: uuid.UUID) -> Interaction:
        return self._load(interaction_id)

    def create_interaction(self, data: InteractionCreate) -> Interaction:
        self._validate_links(data.participant_ids, data.topic_ids)
        payload = data.model_dump(exclude={"participant_ids", "topic_ids"})
        interaction = self.interactions.create(Interaction(**payload))
        for person_id in data.participant_ids:
            self.db.add(InteractionParticipant(interaction_id=interaction.id, person_id=person_id))
        for topic_id in data.topic_ids:
            self.db.add(InteractionTopic(interaction_id=interaction.id, topic_id=topic_id))
        if data.follow_up:
            for person_id in data.participant_ids:
                self.db.add(
                    FollowUpTask(
                        person_id=person_id,
                        interaction_id=interaction.id,
                        title=data.follow_up,
                    )
                )
        self.db.flush()
        return self._load(interaction.id)

    def update_interaction(
        self, interaction_id: uuid.UUID, data: InteractionUpdate
    ) -> Interaction:
        interaction = self._load(interaction_id)
        values = data.model_dump(
            exclude_unset=True, exclude={"participant_ids", "topic_ids"}
        )
        for key, value in values.items():
            setattr(interaction, key, value)
        if data.participant_ids is not None:
            self._validate_links(data.participant_ids, data.topic_ids or [])
            for row in self.db.execute(
                select(InteractionParticipant).where(
                    InteractionParticipant.interaction_id == interaction_id
                )
            ).scalars():
                self.db.delete(row)
            for person_id in data.participant_ids:
                self.db.add(
                    InteractionParticipant(interaction_id=interaction_id, person_id=person_id)
                )
        if data.topic_ids is not None:
            for row in self.db.execute(
                select(InteractionTopic).where(
                    InteractionTopic.interaction_id == interaction_id
                )
            ).scalars():
                self.db.delete(row)
            for topic_id in data.topic_ids:
                self.db.add(InteractionTopic(interaction_id=interaction_id, topic_id=topic_id))
        self.db.flush()
        self.db.expire(interaction)
        return self._load(interaction_id)

    def delete_interaction(self, interaction_id: uuid.UUID) -> None:
        if not self.interactions.soft_delete(interaction_id):
            raise AppError("NOT_FOUND", status_code=404)
