"""全局搜索 API。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.services.search_service import search

router = APIRouter()


@router.get("/search")
def global_search(
    q: str = Query(min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict:
    return success_response(search(db, q, limit))
