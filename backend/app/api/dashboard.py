"""首页统计、提醒与周报 API。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.services import memory_service

router = APIRouter()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)) -> dict:
    return success_response(memory_service.dashboard(db))


@router.post("/reports/weekly")
async def weekly_report(db: Session = Depends(get_db)) -> dict:
    report = await memory_service.weekly_report(db)
    return success_response({"report": report})
