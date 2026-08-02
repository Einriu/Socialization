"""话题基础 Schema（R2 完整扩展，R1 仅用于互动关联展示）。"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class TopicLite(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
