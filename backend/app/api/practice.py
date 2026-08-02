"""社交练习 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.p2 import (
    BackgroundGenerate,
    PracticeScenarioCreate,
    PracticeSend,
    PracticeSessionCreate,
)
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
                "channel": item.channel,
                "tags": item.tags or [],
                "custom_prompt": item.custom_prompt,
                "participants": item.participants or [],
            }
            for item in items
        ]
    )


@router.post("/practice/scenarios")
def create_scenario(
    data: PracticeScenarioCreate, db: Session = Depends(get_db)
) -> dict:
    item = practice_service.create_custom_scenario(db, data)
    return success_response(
        {
            "id": str(item.id),
            "title": item.title,
            "channel": item.channel,
            "tags": item.tags or [],
        }
    )


@router.get("/practice/tag-library")
def tag_library() -> dict:
    return success_response(practice_service.TAG_LIBRARY)


@router.post("/practice/generate-background")
async def generate_background(
    data: BackgroundGenerate, db: Session = Depends(get_db)
) -> dict:
    background = await practice_service.generate_background(db, data)
    return success_response({"background": background})


@router.post("/practice/sessions")
def create_session(data: PracticeSessionCreate, db: Session = Depends(get_db)) -> dict:
    session = practice_service.create_session(db, data)
    return success_response(
        {
            "id": str(session.id),
            "title": session.title,
            "channel": session.channel,
            "tags": session.tags or [],
            "custom_prompt": session.custom_prompt,
            "participants": session.participants or [],
        }
    )


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
                "channel": item.channel,
                "tags": item.tags or [],
                "custom_prompt": item.custom_prompt,
                "participants": item.participants or [],
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
