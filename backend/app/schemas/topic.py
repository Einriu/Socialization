"""话题、分类与笔记 Schema。"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.person import PersonLite


class TopicLite(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class TopicCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    parent_id: uuid.UUID | None = None


class TopicCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    parent_id: uuid.UUID | None = None


class TopicCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None
    created_at: datetime
    children: list[TopicCategoryRead] = Field(default_factory=list)


class TopicCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category_id: uuid.UUID | None = None
    description: str | None = None
    mastery_level: int = Field(default=1, ge=1, le=6)


class TopicUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category_id: uuid.UUID | None = None
    description: str | None = None
    mastery_level: int | None = Field(default=None, ge=1, le=6)
    last_reviewed_at: datetime | None = None


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category_id: uuid.UUID | None
    description: str | None
    mastery_level: int
    last_reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    persons: list[PersonLite] = Field(default_factory=list)


class TopicPersonsUpdate(BaseModel):
    person_ids: list[uuid.UUID] = Field(default_factory=list)


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    topic_id: uuid.UUID
    content_json: dict | None
    plain_text: str | None
    updated_at: datetime | None


class NoteSave(BaseModel):
    content_json: dict
    plain_text: str
    expected_updated_at: str | None = None
