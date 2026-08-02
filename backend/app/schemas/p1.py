"""P1 Schema：文件、搜索与自定义字段。"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_size: int
    mime_type: str | None
    sha256: str
    status: str
    parse_version: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0
    person_ids: list[uuid.UUID] = Field(default_factory=list)
    topic_ids: list[uuid.UUID] = Field(default_factory=list)


class DocumentChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chunk_index: int
    page_start: int | None
    page_end: int | None
    heading_path: str | None
    content: str
    token_count: int | None


class DocumentLinksUpdate(BaseModel):
    person_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None


FieldType = Literal[
    "text",
    "textarea",
    "number",
    "date",
    "select",
    "multi_select",
    "boolean",
    "link",
    "file",
    "person",
]


class CustomFieldCreate(BaseModel):
    field_type: FieldType = "text"
    name: str = Field(min_length=1, max_length=100)
    group_name: str | None = Field(default=None, max_length=50)
    options: list[str] | None = None
    is_required: bool = False
    sort_order: int = 0


class CustomFieldUpdate(BaseModel):
    field_type: FieldType | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)
    group_name: str | None = Field(default=None, max_length=50)
    options: list[str] | None = None
    is_required: bool | None = None
    sort_order: int | None = None


class CustomFieldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    field_type: str
    name: str
    group_name: str | None
    options: list | None
    is_required: bool
    sort_order: int
    created_at: datetime


class CustomFieldValueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    custom_field_id: uuid.UUID
    person_id: uuid.UUID
    value: object | None


class CustomFieldValueUpdate(BaseModel):
    values: dict[uuid.UUID, object] = Field(default_factory=dict)


class SearchResult(BaseModel):
    persons: list[dict] = Field(default_factory=list)
    topics: list[dict] = Field(default_factory=list)
    interactions: list[dict] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    documents: list[dict] = Field(default_factory=list)
