"""P2 社交能力：简报、互动提取与确认、复盘。"""

from __future__ import annotations

import json
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.encryption import decrypt_text
from app.core.exceptions import AppError
from app.models.ai import AIModel, AIProvider
from app.models.interaction import Interaction, InteractionParticipant
from app.models.p2 import InteractionExtractedFact
from app.models.person import FollowUpTask, Person, PersonFact
from app.models.support import PromptTemplate
from app.providers.base import ChatMessage, ChatRequest, ProviderError
from app.providers.registry import build_provider


def _resolve_chat(db: Session) -> tuple[object, str]:
    """找到可用的聊天提供商与模型，返回 (adapter, model_id)。"""
    row = (
        db.execute(
            select(AIModel, AIProvider)
            .join(AIProvider, AIProvider.id == AIModel.provider_id)
            .where(
                AIModel.model_type == "chat",
                AIModel.enabled.is_(True),
                AIProvider.deleted_at.is_(None),
                AIProvider.enabled.is_(True),
                AIProvider.encrypted_api_key.is_not(None),
            )
        )
        .first()
    )
    if row is None:
        raise AppError("AI_PROVIDER_ERROR", "请先配置可用的聊天提供商与模型", status_code=400)
    model, provider = row
    try:
        adapter = build_provider(provider, decrypt_text(provider.encrypted_api_key))
    except Exception as exc:  # noqa: BLE001
        raise AppError("AI_PROVIDER_ERROR", "API Key 解密失败", status_code=400) from exc
    return adapter, model.model_id


async def _chat(db: Session, template_type: str, content: str) -> str:
    adapter, model_id = _resolve_chat(db)
    template = db.execute(
        select(PromptTemplate).where(PromptTemplate.template_type == template_type)
    ).scalar_one_or_none()
    system = template.content if template is not None else "你是一位友好的社交助手。"
    try:
        response = await adapter.chat(
            ChatRequest(
                model=model_id,
                messages=[
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=content),
                ],
            )
        )
    except ProviderError as exc:
        raise AppError("AI_PROVIDER_ERROR", str(exc), status_code=400) from exc
    return response.content.strip()


async def generate_briefing(db: Session, person_id: uuid.UUID) -> str:
    person = db.get(Person, person_id)
    if person is None or person.deleted_at is not None:
        raise AppError("NOT_FOUND", status_code=404)
    facts = db.execute(
        select(PersonFact).where(
            PersonFact.person_id == person_id,
            PersonFact.confidence.in_(["confirmed", "user_observation"]),
            PersonFact.is_sensitive.is_(False),
        )
    ).scalars()
    interactions = db.execute(
        select(Interaction)
        .join(InteractionParticipant)
        .where(
            InteractionParticipant.person_id == person_id,
            Interaction.deleted_at.is_(None),
        )
        .order_by(Interaction.occurred_at.desc())
        .limit(3)
    ).scalars()
    content = "\n".join(
        [
            (
                f"人物：{person.name}（关系：{person.relationship_type or '未知'}，"
                f"熟悉度 {person.familiarity_level}/6）"
            ),
            "已确认事实：",
            *[f"- {fact.fact_type}：{fact.content}" for fact in facts],
            "最近互动：",
            *[
                f"- {item.occurred_at.isoformat()} {item.title}（{item.summary or ''}）"
                for item in interactions
            ],
            "请生成聊天简报：开场方式、可延续话题、避免重复询问的内容、本次聊天目标与边界提醒。",
        ]
    )
    return await _chat(db, "chat_prep", content)


async def extract_interaction(
    db: Session, interaction_id: uuid.UUID
) -> list[InteractionExtractedFact]:
    interaction = db.get(Interaction, interaction_id)
    if interaction is None or interaction.deleted_at is not None:
        raise AppError("NOT_FOUND", status_code=404)
    participants = db.execute(
        select(Person)
        .join(InteractionParticipant)
        .where(InteractionParticipant.interaction_id == interaction_id)
    ).scalars()
    participants = list(participants)
    content = "\n".join(
        [
            f"互动：{interaction.title}（{interaction.occurred_at.isoformat()}）",
            f"摘要：{interaction.summary or ''}",
            f"对方新增信息：{interaction.new_info or ''}",
            f"后续事项：{interaction.follow_up or ''}",
            "请以 JSON 数组输出建议，每项形如 "
            '{"kind":"fact|follow_up","fact_type":"喜好等","content":"内容"}，不要输出其他文字。',
        ]
    )
    raw = await _chat(db, "interaction_extract", content)
    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        items = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        raise AppError("AI_PROVIDER_ERROR", "AI 返回格式无法解析", status_code=400) from None
    created: list[InteractionExtractedFact] = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict) or not item.get("content"):
            continue
        person = participants[0] if participants else None
        row = InteractionExtractedFact(
            interaction_id=interaction_id,
            person_id=person.id if person else None,
            kind="follow_up" if item.get("kind") == "follow_up" else "fact",
            fact_type=str(item.get("fact_type") or "其他"),
            content=str(item["content"]),
        )
        db.add(row)
        created.append(row)
    db.flush()
    return created


def confirm_extractions(db: Session, ids: list[uuid.UUID]) -> dict:
    confirmed = 0
    for row in db.execute(
        select(InteractionExtractedFact).where(InteractionExtractedFact.id.in_(ids))
    ).scalars():
        if row.status != "pending":
            continue
        if row.kind == "follow_up":
            db.add(
                FollowUpTask(
                    person_id=row.person_id,
                    interaction_id=row.interaction_id,
                    title=row.content,
                )
            )
        elif row.person_id is not None:
            db.add(
                PersonFact(
                    person_id=row.person_id,
                    fact_type=row.fact_type,
                    content=row.content,
                    source_type="ai_inference",
                    confidence="ai_inference",
                )
            )
        row.status = "confirmed"
        confirmed += 1
    db.flush()
    return {"confirmed": confirmed}


def list_pending_extractions(
    db: Session, interaction_id: uuid.UUID
) -> list[InteractionExtractedFact]:
    return list(
        db.execute(
            select(InteractionExtractedFact)
            .where(
                InteractionExtractedFact.interaction_id == interaction_id,
                InteractionExtractedFact.status == "pending",
            )
            .order_by(InteractionExtractedFact.created_at.asc())
        ).scalars()
    )


async def review_interaction(db: Session, interaction_id: uuid.UUID) -> str:
    interaction = db.get(Interaction, interaction_id)
    if interaction is None or interaction.deleted_at is not None:
        raise AppError("NOT_FOUND", status_code=404)
    content = "\n".join(
        [
            f"互动：{interaction.title}",
            f"摘要：{interaction.summary or ''}",
            f"我的表现：{interaction.my_performance or ''}",
            f"正面反馈：{interaction.positive_feedback or ''}",
            f"冷场或问题：{interaction.awkward_points or ''}",
            "请从倾听、追问、表达、共情等角度复盘，给出具体反馈与下次改进建议。",
        ]
    )
    return await _chat(db, "chat_review", content)
