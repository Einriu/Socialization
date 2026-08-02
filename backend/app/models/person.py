"""人物、标签、事实、重要日期与待跟进模型。"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UTCDateTime, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interaction import Interaction
    from app.models.topic import Topic


class Person(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """人物档案。"""

    __tablename__ = "persons"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    nickname: Mapped[str | None] = mapped_column(String(100))
    avatar_path: Mapped[str | None] = mapped_column(Text)
    relationship_type: Mapped[str | None] = mapped_column(String(50))
    familiarity_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    met_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True))
    met_location: Mapped[str | None] = mapped_column(Text)
    met_via: Mapped[str | None] = mapped_column(Text)
    organization: Mapped[str | None] = mapped_column(String(200))
    occupation: Mapped[str | None] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text)
    privacy_level: Mapped[str] = mapped_column(String(20), nullable=False, default="private")
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    facts: Mapped[list[PersonFact]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
    tags: Mapped[list[Tag]] = relationship(secondary="person_tags", back_populates="persons")
    dates: Mapped[list[ImportantDate]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
    follow_ups: Mapped[list[FollowUpTask]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
    interactions: Mapped[list[Interaction]] = relationship(
        secondary="interaction_participants", back_populates="persons"
    )
    topics: Mapped[list[Topic]] = relationship(
        secondary="topic_person_links", back_populates="persons"
    )


class Tag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """标签。"""

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    color: Mapped[str | None] = mapped_column(String(20))
    group_name: Mapped[str | None] = mapped_column(String(50))
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    persons: Mapped[list[Person]] = relationship(secondary="person_tags", back_populates="tags")


class PersonTag(Base):
    """人物-标签 多对多关联。"""

    __tablename__ = "person_tags"
    __table_args__ = (UniqueConstraint("person_id", "tag_id", name="uq_person_tags"),)

    person_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("persons.id"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tags.id"), primary_key=True)


class PersonFact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """人物事实：喜好/禁忌/性格印象等，带来源与置信度。"""

    __tablename__ = "person_facts"

    person_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("persons.id"), nullable=False, index=True
    )
    fact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, default="user")
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    is_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    person: Mapped[Person] = relationship(back_populates="facts")


class ImportantDate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """重要日期：生日、纪念日等。"""

    __tablename__ = "important_dates"

    person_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("persons.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    kind: Mapped[str | None] = mapped_column(String(30))
    date_value: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    person: Mapped[Person] = relationship(back_populates="dates")


class FollowUpTask(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """待跟进事项。"""

    __tablename__ = "follow_up_tasks"

    person_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("persons.id"), index=True
    )
    interaction_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("interactions.id")
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True))
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    person: Mapped[Person | None] = relationship(back_populates="follow_ups")
    interaction: Mapped[Interaction | None] = relationship()
