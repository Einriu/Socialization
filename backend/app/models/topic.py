"""话题知识库模型。"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UTCDateTime, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interaction import Interaction
    from app.models.person import Person


class TopicCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """话题分类（自引用树）。"""

    __tablename__ = "topic_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("topic_categories.id")
    )

    children: Mapped[list[TopicCategory]] = relationship()


class Topic(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """话题。"""

    __tablename__ = "topics"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("topic_categories.id")
    )
    description: Mapped[str | None] = mapped_column(Text)
    mastery_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True))

    category: Mapped[TopicCategory | None] = relationship()
    notes: Mapped[list[TopicNote]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )
    persons: Mapped[list[Person]] = relationship(
        secondary="topic_person_links", back_populates="topics"
    )
    interactions: Mapped[list[Interaction]] = relationship(
        secondary="interaction_topics", back_populates="topics"
    )


class TopicNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """话题笔记（Tiptap JSON + 纯文本）。"""

    __tablename__ = "topic_notes"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("topics.id"), nullable=False, unique=True, index=True
    )
    content_json: Mapped[dict | None] = mapped_column(JSON)
    plain_text: Mapped[str | None] = mapped_column(Text)

    topic: Mapped[Topic] = relationship(back_populates="notes")


class TopicPersonLink(Base):
    """话题-人物 多对多关联。"""

    __tablename__ = "topic_person_links"
    __table_args__ = (UniqueConstraint("topic_id", "person_id", name="uq_topic_person_links"),)

    topic_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("topics.id"), primary_key=True)
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("persons.id"), primary_key=True)
