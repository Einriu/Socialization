"""AI 提供商与模型 Schema。"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ProviderType = Literal["openai_compatible", "deepseek", "openai"]


class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    provider_type: ProviderType = "openai_compatible"
    base_url: str | None = None
    api_key: str | None = None
    custom_headers: dict | None = None
    enabled: bool = True
    timeout_seconds: int = Field(default=60, ge=1, le=600)
    max_retries: int = Field(default=2, ge=0, le=5)
    proxy: str | None = None
    default_model_id: uuid.UUID | None = None


class ProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    provider_type: ProviderType | None = None
    base_url: str | None = None
    api_key: str | None = None
    clear_api_key: bool = False
    custom_headers: dict | None = None
    enabled: bool | None = None
    timeout_seconds: int | None = Field(default=None, ge=1, le=600)
    max_retries: int | None = Field(default=None, ge=0, le=5)
    proxy: str | None = None
    default_model_id: uuid.UUID | None = None


class ProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    provider_type: str
    base_url: str | None
    enabled: bool
    timeout_seconds: int
    max_retries: int
    proxy: str | None
    default_model_id: uuid.UUID | None
    last_tested_at: datetime | None
    created_at: datetime
    updated_at: datetime
    has_api_key: bool = False
    key_hint: str | None = None


class ModelCreate(BaseModel):
    model_id: str = Field(min_length=1, max_length=100)
    display_name: str | None = Field(default=None, max_length=100)
    model_type: Literal["chat", "embedding", "reasoning", "other"] = "chat"
    context_length: int | None = None
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_json: bool = False
    supports_vision: bool = False
    supports_reasoning: bool = False
    input_price_note: str | None = Field(default=None, max_length=200)
    output_price_note: str | None = Field(default=None, max_length=200)
    enabled: bool = True


class ModelUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    model_type: Literal["chat", "embedding", "reasoning", "other"] | None = None
    context_length: int | None = None
    supports_streaming: bool | None = None
    supports_tools: bool | None = None
    supports_json: bool | None = None
    supports_vision: bool | None = None
    supports_reasoning: bool | None = None
    input_price_note: str | None = Field(default=None, max_length=200)
    output_price_note: str | None = Field(default=None, max_length=200)
    enabled: bool | None = None


class ModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider_id: uuid.UUID
    model_id: str
    display_name: str | None
    model_type: str
    context_length: int | None
    supports_streaming: bool
    supports_tools: bool
    supports_json: bool
    supports_vision: bool
    supports_reasoning: bool
    input_price_note: str | None
    output_price_note: str | None
    enabled: bool
    source: str
    created_at: datetime
