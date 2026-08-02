"""AI 会话 API（含 SSE 流式对话）。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.common import Page
from app.schemas.conversation import (
    ConversationCreate,
    ConversationLinksUpdate,
    ConversationMessageRead,
    ConversationRead,
    ConversationUpdate,
)
from app.services.conversation_service import ConversationService

router = APIRouter()


class SendMessage(BaseModel):
    content: str = Field(min_length=1)
    model_id: uuid.UUID | None = None


@router.get("/conversations")
def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, total = ConversationService(db).list_conversations(page, page_size)
    payload = Page[ConversationRead](
        items=[ConversationRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/conversations")
def create_conversation(
    data: ConversationCreate, db: Session = Depends(get_db)
) -> dict:
    item = ConversationService(db).create_conversation(data)
    return success_response(ConversationRead.model_validate(item))


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: uuid.UUID, db: Session = Depends(get_db)
) -> dict:
    item = ConversationService(db).get_conversation(conversation_id)
    return success_response(ConversationRead.model_validate(item))


@router.patch("/conversations/{conversation_id}")
def update_conversation(
    conversation_id: uuid.UUID,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
) -> dict:
    item = ConversationService(db).update_conversation(conversation_id, data)
    return success_response(ConversationRead.model_validate(item))


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: uuid.UUID, db: Session = Depends(get_db)
) -> dict:
    ConversationService(db).delete_conversation(conversation_id)
    return success_response(None, "已删除")


@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    items, total = ConversationService(db).list_messages(
        conversation_id, page, page_size
    )
    payload = Page[ConversationMessageRead](
        items=[ConversationMessageRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: uuid.UUID, data: SendMessage, db: Session = Depends(get_db)
) -> StreamingResponse:
    service = ConversationService(db)
    stream = service.stream_send(conversation_id, data.content, data.model_id)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/conversations/{conversation_id}/cancel")
def cancel_generation(conversation_id: uuid.UUID) -> dict:
    ConversationService.cancel(conversation_id)
    return success_response(None, "已请求停止")


@router.post("/conversations/{conversation_id}/messages/{message_id}/regenerate")
async def regenerate_message(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    service = ConversationService(db)
    stream = service.stream_regenerate(conversation_id, message_id)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.put("/conversations/{conversation_id}/links")
def set_links(
    conversation_id: uuid.UUID,
    data: ConversationLinksUpdate,
    db: Session = Depends(get_db),
) -> dict:
    links = ConversationService(db).set_links(conversation_id, data)
    return success_response(
        [
            {"id": str(link.id), "person_id": link.person_id, "topic_id": link.topic_id}
            for link in links
        ]
    )


@router.get("/conversations/{conversation_id}/links")
def get_links(conversation_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    conversation = ConversationService(db).get_conversation(conversation_id)
    return success_response(
        [
            {"id": str(link.id), "person_id": link.person_id, "topic_id": link.topic_id}
            for link in conversation.links
        ]
    )


@router.post("/conversations/{conversation_id}/summarize")
async def summarize_conversation(
    conversation_id: uuid.UUID, db: Session = Depends(get_db)
) -> dict:
    summary = await ConversationService(db).summarize(conversation_id)
    return success_response({"summary": summary})
