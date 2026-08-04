"""P2 Schema。"""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BriefingResponse(BaseModel):
    briefing: str


class ReviewResponse(BaseModel):
    review: str


class ConfirmExtractions(BaseModel):
    ids: list[uuid.UUID] = Field(default_factory=list)


class PracticeSessionCreate(BaseModel):
    scenario_id: uuid.UUID | None = None
    title: str | None = None
    channel: Literal["online", "offline"] = "offline"
    tags: list[str] = Field(default_factory=list)
    custom_prompt: str | None = None
    participants: list[dict] = Field(default_factory=list)


class PracticeScenarioCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    channel: Literal["online", "offline"] = "offline"
    tags: list[str] = Field(default_factory=list)
    custom_prompt: str | None = None
    participants: list[dict] = Field(default_factory=list)


class BackgroundGenerate(BaseModel):
    channel: Literal["online", "offline"] = "offline"
    tags: list[str] = Field(default_factory=list)
    custom_prompt: str | None = None
    person_ids: list[uuid.UUID] = Field(default_factory=list)
    roles: list[dict] = Field(default_factory=list)


class PracticeSend(BaseModel):
    content: str = Field(min_length=1)


class MemoryCreate(BaseModel):
    kind: Literal["preference", "goal", "habit", "other"] = "preference"
    content: str = Field(min_length=1)
    person_id: uuid.UUID | None = None


class MemoryUpdate(BaseModel):
    status: Literal["accepted", "ignored"] | None = None
    content: str | None = None


class UserProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    expression_preferences: dict | None
    social_goals: dict | None


class UserProfileUpdate(BaseModel):
    expression_preferences: dict | None = None
    social_goals: dict | None = None


class DashboardData(BaseModel):
    persons: int = 0
    interactions: int = 0
    topics: int = 0
    documents: int = 0
    due_followups: list[dict] = Field(default_factory=list)
    due_reviews: list[dict] = Field(default_factory=list)
    recent_interactions: list[dict] = Field(default_factory=list)
