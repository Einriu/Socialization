"""人物、事实、重要日期、待跟进与时间线 Schema。"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag import TagRead

SourceType = Literal["user", "person", "ai_inference"]
Confidence = Literal["confirmed", "user_observation", "unconfirmed", "ai_inference", "outdated"]


class PersonBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    nickname: str | None = Field(default=None, max_length=100)
    avatar_path: str | None = None
    relationship_type: str | None = Field(default=None, max_length=50)
    familiarity_level: int = Field(default=1, ge=1, le=6)
    met_at: datetime | None = None
    met_location: str | None = None
    met_via: str | None = None
    organization: str | None = Field(default=None, max_length=200)
    occupation: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    summary: str | None = None
    privacy_level: Literal["private", "protected", "public"] = "private"
    archived: bool = False


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    nickname: str | None = Field(default=None, max_length=100)
    avatar_path: str | None = None
    relationship_type: str | None = Field(default=None, max_length=50)
    familiarity_level: int | None = Field(default=None, ge=1, le=6)
    met_at: datetime | None = None
    met_location: str | None = None
    met_via: str | None = None
    organization: str | None = Field(default=None, max_length=200)
    occupation: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    summary: str | None = None
    privacy_level: Literal["private", "protected", "public"] | None = None
    archived: bool | None = None


class PersonRead(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = Field(default_factory=list)


class PersonLite(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class PersonFactCreate(BaseModel):
    fact_type: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)
    source_type: SourceType = "user"
    source_id: uuid.UUID | None = None
    confidence: Confidence = "confirmed"
    is_sensitive: bool = False


class PersonFactUpdate(BaseModel):
    fact_type: str | None = Field(default=None, min_length=1, max_length=50)
    content: str | None = Field(default=None, min_length=1)
    source_type: SourceType | None = None
    source_id: uuid.UUID | None = None
    confidence: Confidence | None = None
    is_sensitive: bool | None = None


class PersonFactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    person_id: uuid.UUID
    fact_type: str
    content: str
    source_type: str
    source_id: uuid.UUID | None
    confidence: str
    is_sensitive: bool
    created_at: datetime
    updated_at: datetime


class ImportantDateCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    kind: str | None = Field(default=None, max_length=30)
    date_value: date
    note: str | None = None


class ImportantDateUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    kind: str | None = Field(default=None, max_length=30)
    date_value: date | None = None
    note: str | None = None


class ImportantDateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    person_id: uuid.UUID
    title: str
    kind: str | None
    date_value: date
    note: str | None
    created_at: datetime


class FollowUpCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    due_at: datetime | None = None
    completed: bool = False


class FollowUpUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    due_at: datetime | None = None
    completed: bool | None = None


class FollowUpRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    person_id: uuid.UUID | None
    interaction_id: uuid.UUID | None
    title: str
    due_at: datetime | None
    completed: bool
    created_at: datetime
    updated_at: datetime


class TimelineItem(BaseModel):
    type: Literal["interaction", "fact", "important_date"]
    id: uuid.UUID
    title: str
    occurred_at: datetime
    summary: str | None = None
