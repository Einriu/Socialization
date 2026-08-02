"""标签 Schema。"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str | None = Field(default=None, max_length=20)
    group_name: str | None = Field(default=None, max_length=50)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = Field(default=None, max_length=20)
    group_name: str | None = Field(default=None, max_length=50)


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    color: str | None
    group_name: str | None
    is_system: bool
    created_at: datetime
    updated_at: datetime


class PersonTagsUpdate(BaseModel):
    tag_ids: list[uuid.UUID] = Field(default_factory=list)
