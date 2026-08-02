"""复习计划 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.services import review_service

router = APIRouter()


@router.get("/reviews/due")
def due_reviews(db: Session = Depends(get_db)) -> dict:
    return success_response(review_service.list_due_reviews(db))


@router.get("/reviews")
def reviews(db: Session = Depends(get_db)) -> dict:
    return success_response(review_service.list_reviews(db))


@router.post("/reviews/{task_id}/answer")
def answer(
    task_id: uuid.UUID,
    rating: str = Query(min_length=1),
    db: Session = Depends(get_db),
) -> dict:
    return success_response(review_service.answer_review(db, task_id, rating))
