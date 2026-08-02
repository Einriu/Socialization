"""互动记录 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.common import Page
from app.schemas.interaction import InteractionCreate, InteractionRead, InteractionUpdate
from app.schemas.p2 import ConfirmExtractions
from app.services.interaction_service import InteractionService
from app.services.social_service import (
    confirm_extractions,
    extract_interaction,
    list_pending_extractions,
    review_interaction,
)

router = APIRouter()


@router.get("/interactions")
def list_interactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    person_id: uuid.UUID | None = None,
    topic_id: uuid.UUID | None = None,
    start: str | None = None,
    end: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    items, total = InteractionService(db).list_interactions(
        page, page_size, person_id, topic_id, start, end
    )
    payload = Page[InteractionRead](
        items=[InteractionRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/interactions")
def create_interaction(
    data: InteractionCreate, db: Session = Depends(get_db)
) -> dict:
    item = InteractionService(db).create_interaction(data)
    return success_response(InteractionRead.model_validate(item))


@router.get("/interactions/{interaction_id}")
def get_interaction(interaction_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    item = InteractionService(db).get_interaction(interaction_id)
    return success_response(InteractionRead.model_validate(item))


@router.patch("/interactions/{interaction_id}")
def update_interaction(
    interaction_id: uuid.UUID,
    data: InteractionUpdate,
    db: Session = Depends(get_db),
) -> dict:
    item = InteractionService(db).update_interaction(interaction_id, data)
    return success_response(InteractionRead.model_validate(item))


@router.delete("/interactions/{interaction_id}")
def delete_interaction(
    interaction_id: uuid.UUID, db: Session = Depends(get_db)
) -> Response:
    InteractionService(db).delete_interaction(interaction_id)
    return Response(status_code=204)


@router.post("/interactions/{interaction_id}/extract")
async def extract_facts(interaction_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    items = await extract_interaction(db, interaction_id)
    return success_response(
        [
            {
                "id": str(item.id),
                "kind": item.kind,
                "fact_type": item.fact_type,
                "content": item.content,
                "status": item.status,
            }
            for item in items
        ]
    )


@router.get("/interactions/{interaction_id}/extractions")
def pending_extractions(interaction_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    items = list_pending_extractions(db, interaction_id)
    return success_response(
        [
            {
                "id": str(item.id),
                "kind": item.kind,
                "fact_type": item.fact_type,
                "content": item.content,
                "status": item.status,
            }
            for item in items
        ]
    )


@router.post("/interactions/{interaction_id}/confirm-extractions")
def confirm_facts(
    interaction_id: uuid.UUID,
    data: ConfirmExtractions,
    db: Session = Depends(get_db),
) -> dict:
    result = confirm_extractions(db, data.ids)
    return success_response(result)


@router.post("/interactions/{interaction_id}/review")
async def review(interaction_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    text = await review_interaction(db, interaction_id)
    return success_response({"review": text})
