"""互动记录模型。"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UTCDateTime,
    UUIDPrimaryKeyMixin,
    utcnow,
)

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.topic import Topic


class Interaction(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """一次互动（聊天/电话/聚会等）。"""

    __tablename__ = "interactions"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow, index=True
    )
    location: Mapped[str | None] = mapped_column(Text)
    interaction_type: Mapped[str] = mapped_column(String(30), nullable=False, default="chat")
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    summary: Mapped[str | None] = mapped_column(Text)
    new_info: Mapped[str | None] = mapped_column(Text)
    mood_state: Mapped[str | None] = mapped_column(Text)
    my_performance: Mapped[str | None] = mapped_column(Text)
    positive_feedback: Mapped[str | None] = mapped_column(Text)
    awkward_points: Mapped[str | None] = mapped_column(Text)
    follow_up: Mapped[str | None] = mapped_column(Text)
    privacy_level: Mapped[str] = mapped_column(String(20), nullable=False, default="private")

    persons: Mapped[list[Person]] = relationship(
        secondary="interaction_participants", back_populates="interactions"
    )
    topics: Mapped[list[Topic]] = relationship(
        secondary="interaction_topics", back_populates="interactions"
    )


class InteractionParticipant(Base):
    """互动-人物 多对多关联。"""

    __tablename__ = "interaction_participants"
    __table_args__ = (
        UniqueConstraint("interaction_id", "person_id", name="uq_interaction_participants"),
    )

    interaction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("interactions.id"), primary_key=True
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("persons.id"), primary_key=True
    )


class InteractionTopic(Base):
    """互动-话题 多对多关联。"""

    __tablename__ = "interaction_topics"
    __table_args__ = (UniqueConstraint("interaction_id", "topic_id", name="uq_interaction_topics"),)

    interaction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("interactions.id"), primary_key=True
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("topics.id"), primary_key=True
    )
