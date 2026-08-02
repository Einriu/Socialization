"""社交练习 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.p2 import PracticeSend, PracticeSessionCreate
from app.services import practice_service

router = APIRouter()


@router.get("/practice/scenarios")
def scenarios(db: Session = Depends(get_db)) -> dict:
    items = practice_service.list_scenarios(db)
    return success_response(
        [
            {
                "id": str(item.id),
                "scenario_type": item.scenario_type,
                "title": item.title,
                "description": item.description,
            }
            for item in items
        ]
    )


@router.post("/practice/sessions")
def create_session(data: PracticeSessionCreate, db: Session = Depends(get_db)) -> dict:
    session = practice_service.create_session(db, data)
    return success_response({"id": str(session.id), "title": session.title})


@router.get("/practice/sessions")
def sessions(db: Session = Depends(get_db)) -> dict:
    items = practice_service.list_sessions(db)
    return success_response(
        [
            {
                "id": str(item.id),
                "title": item.title,
                "status": item.status,
                "scenario_id": str(item.scenario_id),
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ]
    )


@router.get("/practice/sessions/{session_id}/messages")
def messages(session_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    items = practice_service.list_messages(db, session_id)
    return success_response(
        [
            {"id": str(item.id), "role": item.role, "content": item.content}
            for item in items
        ]
    )


@router.post("/practice/sessions/{session_id}/messages")
def send_message(
    session_id: uuid.UUID, data: PracticeSend, db: Session = Depends(get_db)
) -> StreamingResponse:
    stream = practice_service.stream_practice(db, session_id, data.content)
    return StreamingResponse(stream, media_type="text/event-stream")


@router.post("/practice/sessions/{session_id}/evaluate")
async def evaluate(session_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    result = await practice_service.evaluate_session(db, session_id)
    return success_response(result)
