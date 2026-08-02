"""话题、分类与笔记 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.common import Page
from app.schemas.topic import (
    NoteRead,
    NoteSave,
    TopicCategoryCreate,
    TopicCategoryUpdate,
    TopicCreate,
    TopicPersonsUpdate,
    TopicRead,
    TopicUpdate,
)
from app.services.topic_service import TopicService

router = APIRouter()


@router.get("/topic-categories")
def list_categories(db: Session = Depends(get_db)) -> dict:
    return success_response(TopicService(db).category_tree())


@router.post("/topic-categories")
def create_category(
    data: TopicCategoryCreate, db: Session = Depends(get_db)
) -> dict:
    item = TopicService(db).create_category(data)
    return success_response(
        {"id": str(item.id), "name": item.name, "parent_id": item.parent_id}
    )


@router.patch("/topic-categories/{category_id}")
def update_category(
    category_id: uuid.UUID,
    data: TopicCategoryUpdate,
    db: Session = Depends(get_db),
) -> dict:
    item = TopicService(db).update_category(category_id, data)
    return success_response(
        {"id": str(item.id), "name": item.name, "parent_id": item.parent_id}
    )


@router.delete("/topic-categories/{category_id}")
def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    TopicService(db).delete_category(category_id)
    return Response(status_code=204)


@router.get("/topics")
def list_topics(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    category_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> dict:
    items, total = TopicService(db).list_topics(page, page_size, q, category_id)
    payload = Page[TopicRead](
        items=[TopicRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/topics")
def create_topic(data: TopicCreate, db: Session = Depends(get_db)) -> dict:
    item = TopicService(db).create_topic(data)
    return success_response(TopicRead.model_validate(item))


@router.get("/topics/{topic_id}")
def get_topic(topic_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    item = TopicService(db).get_topic(topic_id)
    return success_response(TopicRead.model_validate(item))


@router.patch("/topics/{topic_id}")
def update_topic(
    topic_id: uuid.UUID, data: TopicUpdate, db: Session = Depends(get_db)
) -> dict:
    item = TopicService(db).update_topic(topic_id, data)
    return success_response(TopicRead.model_validate(item))


@router.delete("/topics/{topic_id}")
def delete_topic(topic_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    TopicService(db).delete_topic(topic_id)
    return Response(status_code=204)


@router.put("/topics/{topic_id}/persons")
def set_topic_persons(
    topic_id: uuid.UUID, data: TopicPersonsUpdate, db: Session = Depends(get_db)
) -> dict:
    item = TopicService(db).set_topic_persons(topic_id, data)
    return success_response(TopicRead.model_validate(item))


@router.get("/topics/{topic_id}/notes")
def get_note(topic_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    service = TopicService(db)
    note = service.get_note(topic_id)
    if note is None:
        return success_response(
            NoteRead(topic_id=topic_id, content_json=None, plain_text=None, updated_at=None)
        )
    return success_response(NoteRead.model_validate(note))


@router.put("/topics/{topic_id}/notes")
def save_note(
    topic_id: uuid.UUID, data: NoteSave, db: Session = Depends(get_db)
) -> dict:
    note = TopicService(db).save_note(topic_id, data)
    return success_response(NoteRead.model_validate(note))
