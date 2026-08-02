"""互动记录 Schema。"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.person import PersonLite
from app.schemas.topic import TopicLite


class InteractionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    occurred_at: datetime | None = None
    location: str | None = None
    interaction_type: Literal[
        "face_to_face",
        "phone",
        "wechat",
        "party",
        "work",
        "sports",
        "meal",
        "other",
    ] = "face_to_face"
    duration_minutes: int | None = Field(default=None, ge=0, le=24 * 60)
    summary: str | None = None
    new_info: str | None = None
    mood_state: str | None = None
    my_performance: str | None = None
    positive_feedback: str | None = None
    awkward_points: str | None = None
    follow_up: str | None = None
    privacy_level: Literal["private", "protected", "public"] = "private"
    participant_ids: list[uuid.UUID] = Field(min_length=1)
    topic_ids: list[uuid.UUID] = Field(default_factory=list)


class InteractionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    occurred_at: datetime | None = None
    location: str | None = None
    interaction_type: Literal[
        "face_to_face",
        "phone",
        "wechat",
        "party",
        "work",
        "sports",
        "meal",
        "other",
    ] | None = None
    duration_minutes: int | None = Field(default=None, ge=0, le=24 * 60)
    summary: str | None = None
    new_info: str | None = None
    mood_state: str | None = None
    my_performance: str | None = None
    positive_feedback: str | None = None
    awkward_points: str | None = None
    follow_up: str | None = None
    privacy_level: Literal["private", "protected", "public"] | None = None
    participant_ids: list[uuid.UUID] | None = Field(default=None, min_length=1)
    topic_ids: list[uuid.UUID] | None = None


class InteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    occurred_at: datetime
    location: str | None
    interaction_type: str
    duration_minutes: int | None
    summary: str | None
    new_info: str | None
    mood_state: str | None
    my_performance: str | None
    positive_feedback: str | None
    awkward_points: str | None
    follow_up: str | None
    privacy_level: str
    created_at: datetime
    updated_at: datetime
    persons: list[PersonLite] = Field(default_factory=list)
    topics: list[TopicLite] = Field(default_factory=list)
