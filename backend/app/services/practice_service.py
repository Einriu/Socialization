"""AI 模拟聊天练习与评分。"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.p2 import (
    PracticeEvaluation,
    PracticeMessage,
    PracticeScenario,
    PracticeSession,
)
from app.providers.base import ChatMessage, ChatRequest, ProviderError
from app.schemas.p2 import PracticeSessionCreate
from app.services.social_service import _resolve_chat


def list_scenarios(db: Session) -> list[PracticeScenario]:
    return list(
        db.execute(
            select(PracticeScenario).order_by(PracticeScenario.created_at.asc())
        ).scalars()
    )


def create_session(db: Session, data: PracticeSessionCreate) -> PracticeSession:
    scenario = db.get(PracticeScenario, data.scenario_id)
    if scenario is None:
        raise AppError("NOT_FOUND", "场景不存在", status_code=404)
    session = PracticeSession(
        scenario_id=scenario.id,
        title=data.title or scenario.title,
        status="active",
    )
    db.add(session)
    db.flush()
    return session


def list_sessions(db: Session) -> list[PracticeSession]:
    return list(
        db.execute(
            select(PracticeSession).order_by(PracticeSession.created_at.desc()).limit(50)
        ).scalars()
    )


def list_messages(db: Session, session_id: uuid.UUID) -> list[PracticeMessage]:
    return list(
        db.execute(
            select(PracticeMessage)
            .where(PracticeMessage.session_id == session_id)
            .order_by(PracticeMessage.created_at.asc())
        ).scalars()
    )


async def stream_practice(
    db: Session, session_id: uuid.UUID, content: str
) -> AsyncIterator[str]:
    session = db.get(PracticeSession, session_id)
    if session is None:
        raise AppError("NOT_FOUND", status_code=404)
    scenario = db.get(PracticeScenario, session.scenario_id)
    user_message = PracticeMessage(session_id=session_id, role="user", content=content)
    db.add(user_message)
    db.flush()
    try:
        adapter, model_id = _resolve_chat(db)
    except AppError as exc:
        payload = json.dumps({"type": "error", "message": exc.message}, ensure_ascii=False)
        yield f"data: {payload}\n\n"
        return
    history = list_messages(db, session_id)
    system = (
        f"你正在扮演角色进行社交练习。场景：{scenario.title}。"
        f"角色设定：{json.dumps(scenario.role_params or {}, ensure_ascii=False)}。"
        "请用自然、真实的口吻与用户对话，一次只说 1-3 句话，不要替用户说话。"
    )
    messages = [
        ChatMessage(role="system", content=system),
        *[
            ChatMessage(role=item.role, content=item.content)
            for item in history
        ],
    ]
    request = ChatRequest(model=model_id, messages=messages)
    parts: list[str] = []
    try:
        async for delta in adapter.stream_chat(request):
            parts.append(delta)
            yield f"data: {json.dumps({'type': 'delta', 'content': delta}, ensure_ascii=False)}\n\n"
    except ProviderError as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n\n"
        return
    db.add(PracticeMessage(session_id=session_id, role="assistant", content="".join(parts)))
    db.commit()
    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"


async def evaluate_session(db: Session, session_id: uuid.UUID) -> dict:
    session = db.get(PracticeSession, session_id)
    if session is None:
        raise AppError("NOT_FOUND", status_code=404)
    messages = list_messages(db, session_id)
    transcript = "\n".join(
        f"{'我' if item.role == 'user' else '对方'}：{item.content}" for item in messages
    )
    adapter, model_id = _resolve_chat(db)
    prompt = (
        "请对以下模拟对话从十个维度评分（开场自然度、倾听能力、有效追问、共情表达、"
        "自我表达、话题衔接、边界意识、对话节奏、结束方式、总体舒适度），"
        "每项 1-10 分并给出具体对话证据。以 JSON 输出："
        '{"scores":{"维度":分数,...},"summary":"总体评价与建议"}，不要输出其他文字。\n\n'
        f"{transcript}"
    )
    try:
        response = await adapter.chat(
            ChatRequest(
                model=model_id,
                messages=[ChatMessage(role="user", content=prompt)],
            )
        )
    except ProviderError as exc:
        raise AppError("AI_PROVIDER_ERROR", str(exc), status_code=400) from exc
    raw = response.content.strip()
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        parsed = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        raise AppError("AI_PROVIDER_ERROR", "评分返回格式无法解析", status_code=400) from None
    scores = parsed.get("scores", {})
    summary = parsed.get("summary", "")
    db.add(PracticeEvaluation(session_id=session_id, scores=scores, summary=summary))
    session.status = "completed"
    db.flush()
    return {"scores": scores, "summary": summary}
