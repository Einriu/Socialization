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
from app.models.person import Person, PersonFact
from app.providers.base import ChatMessage, ChatRequest, ProviderError
from app.schemas.p2 import BackgroundGenerate, PracticeScenarioCreate, PracticeSessionCreate
from app.services.social_service import _chat, _resolve_chat

TAG_LIBRARY = {
    "场合": [
        "朋友聚会", "公司年会", "饭局", "婚礼", "同学会", "家庭聚餐", "咖啡馆", "健身房",
        "公园散步", "户外活动", "书店", "展会", "面试", "商务宴请", "相亲", "第一次约会",
        "微信私聊", "微信群聊", "视频通话", "语音通话",
    ],
    "谈话背景": [
        "初次见面", "久别重逢", "求人帮忙", "表达感谢", "道歉", "提离职", "安慰朋友",
        "谈合作", "化解误会", "表白", "拒绝请求", "表达边界", "介绍自己", "冷场救场",
        "分享好消息", "聊近况",
    ],
    "对象类型": [
        "同事", "同学", "朋友", "家人", "上级", "客户", "陌生人", "内向者", "健谈者",
        "异性朋友", "长辈", "晚辈", "群里的新人",
    ],
}

CHANNEL_LABELS = {"online": "线上（微信等）", "offline": "线下社交"}


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
        channel=data.channel,
        tags=data.tags,
        custom_prompt=data.custom_prompt or scenario.custom_prompt,
        participants=data.participants or scenario.participants,
    )
    db.add(session)
    db.flush()
    return session


def create_custom_scenario(db: Session, data: PracticeScenarioCreate) -> PracticeScenario:
    scenario = PracticeScenario(
        scenario_type="custom",
        title=data.title,
        channel=data.channel,
        tags=data.tags,
        custom_prompt=data.custom_prompt,
        participants=data.participants,
        description="自定义练习场景",
    )
    db.add(scenario)
    db.flush()
    return scenario


async def generate_background(db: Session, data: BackgroundGenerate) -> str:
    """根据渠道、标签、人物对象或自定义提示词，生成详细的社交背景故事。"""
    lines = [
        f"交流渠道：{CHANNEL_LABELS.get(data.channel, data.channel)}",
        f"场景标签：{'、'.join(data.tags) if data.tags else '（未指定）'}",
    ]
    if data.person_ids:
        person_lines = []
        for person_id in data.person_ids:
            person = db.get(Person, person_id)
            if person is None:
                continue
            facts = db.execute(
                select(PersonFact)
                .where(
                    PersonFact.person_id == person_id,
                    PersonFact.confidence.in_(["confirmed", "user_observation"]),
                    PersonFact.is_sensitive.is_(False),
                )
                .limit(10)
            ).scalars()
            person_lines.append(
                f"- {person.name}（关系：{person.relationship_type or '未知'}，"
                f"熟悉度 {person.familiarity_level}/6）："
                + "；".join(f"{f.fact_type}：{f.content}" for f in facts)
            )
        lines.append("参与对象（来自我的人物库）：")
        lines.extend(person_lines)
    if data.custom_prompt:
        lines.append(f"自定义场景描述：{data.custom_prompt}")
    prompt = "\n".join(lines) + (
        "\n请基于以上信息，详细扩建一个社交场景背景故事，包括："
        "场景背景与气氛、在场人物及其状态/情绪/对我的态度、彼此的谈话背景故事、"
        "可能的冲突点与破冰切入点。用自然、具体的中文描述。"
    )
    return await _chat(db, "practice", prompt)


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
        f"你正在组织一场多人社交练习。"
        f"渠道：{CHANNEL_LABELS.get(session.channel, session.channel)}。"
        f"场景：{session.custom_prompt or scenario.description or scenario.title}。"
    )
    participants = session.participants or scenario.participants or [{"name": "对方"}]
    role_names = [
        item.get("name", "对方") if isinstance(item, dict) else str(item)
        for item in participants
    ]
    system += (
        "\n在场角色：" + "、".join(role_names) + "。\n"
        "对话规则：\n"
        "1. 一次回复可以包含多个角色的连续发言，每个发言单独成段并以【角色名】开头，"
        "例如：\n【张三】今天天气不错啊。\n【李四】是啊，适合出去走走。\n"
        "2. 角色之间可以互相交谈、回应彼此、自然接话，形成真实的多人群聊；"
        "用户（我）不是唯一发言者，可以随时插话或暂时旁观。\n"
        "3. 每个发言 1-3 句，整条回复 1-6 段，避免冷场；不要替用户（我）说话。"
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
        f"{'我：' if item.role == 'user' else ''}{item.content}" for item in messages
    )
    adapter, model_id = _resolve_chat(db)
    prompt = (
        "请对以下模拟对话从十个维度评分（开场自然度、倾听能力、有效追问、共情表达、"
        "自我表达、话题衔接、边界意识、对话节奏、多角色参与、结束方式、总体舒适度），"
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
