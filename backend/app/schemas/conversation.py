"""AI 会话 Schema。"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    mode: str = Field(default="general", max_length=50)
    provider_id: uuid.UUID | None = None
    model_id: uuid.UUID | None = None


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    provider_id: uuid.UUID | None = None
    model_id: uuid.UUID | None = None
    pinned: bool | None = None
    summary: str | None = None


class ConversationLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    person_id: uuid.UUID | None
    topic_id: uuid.UUID | None


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    mode: str
    provider_id: uuid.UUID | None
    model_id: uuid.UUID | None
    summary: str | None
    pinned: bool
    created_at: datetime
    updated_at: datetime
    links: list[ConversationLinkRead] = Field(default_factory=list)


class ConversationMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str | None
    metadata: dict | None = Field(default=None, validation_alias="metadata_json")
    status: str
    token_input: int | None
    token_output: int | None
    latency_ms: int | None
    generated_by_ai: bool
    created_at: datetime


class ConversationLinksUpdate(BaseModel):
    person_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
