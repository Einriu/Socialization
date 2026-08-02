"""标签 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.common import Page
from app.schemas.tag import TagCreate, TagRead, TagUpdate
from app.services.tag_service import TagService

router = APIRouter()


@router.get("/tags")
def list_tags(db: Session = Depends(get_db)) -> dict:
    items, total = TagService(db).list_tags()
    payload = Page[TagRead](
        items=[TagRead.model_validate(item) for item in items],
        total=total,
        page=1,
        page_size=total,
    )
    return success_response(payload)


@router.post("/tags")
def create_tag(data: TagCreate, db: Session = Depends(get_db)) -> dict:
    tag = TagService(db).create_tag(data)
    return success_response(TagRead.model_validate(tag))


@router.patch("/tags/{tag_id}")
def update_tag(tag_id: uuid.UUID, data: TagUpdate, db: Session = Depends(get_db)) -> dict:
    tag = TagService(db).update_tag(tag_id, data)
    return success_response(TagRead.model_validate(tag))


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    TagService(db).delete_tag(tag_id)
    return Response(status_code=204)
