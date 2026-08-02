"""P2 模型：提取确认、复习、练习、记忆、目标与关系。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UTCDateTime, UUIDPrimaryKeyMixin, utcnow


class InteractionExtractedFact(UUIDPrimaryKeyMixin, Base):
    """互动中 AI 提取的待确认信息。"""

    __tablename__ = "interaction_extracted_facts"

    interaction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("interactions.id"), nullable=False
    )
    person_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("persons.id"))
    kind: Mapped[str] = mapped_column(String(20), nullable=False, default="fact")
    fact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )


class TopicLearningRecord(UUIDPrimaryKeyMixin, Base):
    """话题学习记录。"""

    __tablename__ = "topic_learning_records"

    topic_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("topics.id"), nullable=False)
    learned_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )
    mastery_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )


class ReviewTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """间隔复习任务。"""

    __tablename__ = "review_tasks"

    topic_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("topics.id"), nullable=False)
    due_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False
    )
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True))


class PracticeScenario(UUIDPrimaryKeyMixin, Base):
    """练习场景。"""

    __tablename__ = "practice_scenarios"

    scenario_type: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    role_params: Mapped[dict | None] = mapped_column(JSON)
    channel: Mapped[str] = mapped_column(String(10), nullable=False, default="offline")
    tags: Mapped[list | None] = mapped_column(JSON)
    custom_prompt: Mapped[str | None] = mapped_column(Text)
    participants: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )


class PracticeSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """练习会话。"""

    __tablename__ = "practice_sessions"

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("practice_scenarios.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    channel: Mapped[str] = mapped_column(String(10), nullable=False, default="offline")
    tags: Mapped[list | None] = mapped_column(JSON)
    custom_prompt: Mapped[str | None] = mapped_column(Text)
    participants: Mapped[list | None] = mapped_column(JSON)
    scenario: Mapped[PracticeScenario] = relationship()


class PracticeMessage(UUIDPrimaryKeyMixin, Base):
    """练习对话消息。"""

    __tablename__ = "practice_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("practice_sessions.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )


class PracticeEvaluation(UUIDPrimaryKeyMixin, Base):
    """练习评分。"""

    __tablename__ = "practice_evaluations"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("practice_sessions.id"), nullable=False
    )
    scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False, default=utcnow
    )


class MemoryItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """长期记忆（提议→接受/忽略）。"""

    __tablename__ = "memory_items"

    kind: Mapped[str] = mapped_column(String(30), nullable=False, default="preference")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="proposed")
    person_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("persons.id"))


class UserProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """用户表达偏好与社交目标（单用户）。"""

    __tablename__ = "user_profiles"

    expression_preferences: Mapped[dict | None] = mapped_column(JSON)
    social_goals: Mapped[dict | None] = mapped_column(JSON)


class PersonRelationship(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """人物间关系。"""

    __tablename__ = "person_relationships"

    person_a_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("persons.id"), nullable=False
    )
    person_b_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("persons.id"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
