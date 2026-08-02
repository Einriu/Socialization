"""AI 会话：CRUD、上下文组装、SSE 流式对话、停止与重新生成。"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections import defaultdict
from collections.abc import AsyncIterator

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import SessionLocal
from app.core.encryption import decrypt_text
from app.core.exceptions import AppError
from app.models.ai import AIModel, AIProvider, Conversation, ConversationLink, ConversationMessage
from app.models.person import Person, PersonFact
from app.models.support import PromptTemplate
from app.models.topic import Topic, TopicNote
from app.providers.base import ChatMessage, ChatRequest, ProviderError
from app.providers.registry import build_provider
from app.repositories.base import BaseRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationLinksUpdate,
    ConversationUpdate,
)

_RECENT_MESSAGES = 20
_cancel_events: dict[str, asyncio.Event] = defaultdict(asyncio.Event)


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation


class MessageRepository(BaseRepository[ConversationMessage]):
    model = ConversationMessage


class ConversationService:
    """会话服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)

    # ---- 会话 CRUD ----

    def list_conversations(self, page: int, page_size: int) -> tuple[list[Conversation], int]:
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.links))
            .where(Conversation.deleted_at.is_(None))
        )
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(Conversation.updated_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_conversation(self, conversation_id: uuid.UUID) -> Conversation:
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.links))
            .where(Conversation.id == conversation_id, Conversation.deleted_at.is_(None))
        )
        conversation = self.db.execute(stmt).scalar_one_or_none()
        if conversation is None:
            raise AppError("NOT_FOUND", status_code=404)
        return conversation

    def create_conversation(self, data: ConversationCreate) -> Conversation:
        return self.conversations.create(
            Conversation(
                title=data.title or "新对话",
                mode=data.mode,
                provider_id=data.provider_id,
                model_id=data.model_id,
            )
        )

    def update_conversation(
        self, conversation_id: uuid.UUID, data: ConversationUpdate
    ) -> Conversation:
        values = data.model_dump(exclude_unset=True)
        conversation = self.conversations.update(conversation_id, values)
        if conversation is None:
            raise AppError("NOT_FOUND", status_code=404)
        return conversation

    def delete_conversation(self, conversation_id: uuid.UUID) -> None:
        if not self.conversations.soft_delete(conversation_id):
            raise AppError("NOT_FOUND", status_code=404)

    # ---- 消息与关联 ----

    def list_messages(
        self, conversation_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[ConversationMessage], int]:
        self.get_conversation(conversation_id)
        stmt = select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        )
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(ConversationMessage.created_at.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def set_links(
        self, conversation_id: uuid.UUID, data: ConversationLinksUpdate
    ) -> list[ConversationLink]:
        self.get_conversation(conversation_id)
        for row in self.db.execute(
            select(ConversationLink).where(
                ConversationLink.conversation_id == conversation_id
            )
        ).scalars():
            self.db.delete(row)
        links: list[ConversationLink] = []
        if data.person_id is not None:
            links.append(
                ConversationLink(
                    conversation_id=conversation_id, person_id=data.person_id
                )
            )
        if data.topic_id is not None:
            links.append(ConversationLink(conversation_id=conversation_id, topic_id=data.topic_id))
        for link in links:
            self.db.add(link)
        self.db.flush()
        self.db.expire_all()
        conversation = self.get_conversation(conversation_id)
        return conversation.links

    # ---- 上下文组装 ----

    def _system_prompt(self, mode: str) -> str:
        template = self.db.execute(
            select(PromptTemplate).where(PromptTemplate.template_type == mode)
        ).scalar_one_or_none()
        if template is None:
            template = self.db.execute(
                select(PromptTemplate).where(PromptTemplate.template_type == "general")
            ).scalar_one_or_none()
        return template.content if template is not None else "你是一位友好的社交助手。"

    def _build_context(
        self, conversation: Conversation, user_text: str
    ) -> list[ChatMessage]:
        links = self.db.execute(
            select(ConversationLink).where(
                ConversationLink.conversation_id == conversation.id
            )
        ).scalars()
        link_list = list(links)
        person_link = next((link for link in link_list if link.person_id), None)
        topic_link = next((link for link in link_list if link.topic_id), None)

        system_parts = [self._system_prompt(conversation.mode)]
        if person_link is not None and person_link.person_id is not None:
            person = self.db.get(Person, person_link.person_id)
            if person is not None:
                facts = self.db.execute(
                    select(PersonFact).where(
                        PersonFact.person_id == person.id,
                        PersonFact.confidence.in_(["confirmed", "user_observation"]),
                        PersonFact.is_sensitive.is_(False),
                    )
                ).scalars()
                fact_lines = [f"{fact.fact_type}：{fact.content}" for fact in facts]
                if fact_lines:
                    system_parts.append(
                        f"当前人物档案（{person.name}）：\n" + "\n".join(fact_lines)
                    )
        if topic_link is not None and topic_link.topic_id is not None:
            topic = self.db.get(Topic, topic_link.topic_id)
            if topic is not None:
                note = self.db.execute(
                    select(TopicNote).where(TopicNote.topic_id == topic.id)
                ).scalar_one_or_none()
                summary = (note.plain_text or topic.description or "")[:500]
                if summary:
                    system_parts.append(f"当前话题（{topic.name}）摘要：\n{summary}")

        recent = self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation.id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(_RECENT_MESSAGES)
        ).scalars()
        recent_messages = [
            ChatMessage(role=item.role, content=item.content or "")
            for item in reversed(list(recent))
            if item.role in ("user", "assistant") and item.content
        ]
        return [
            ChatMessage(role="system", content="\n\n".join(system_parts)),
            *recent_messages,
            ChatMessage(role="user", content=user_text),
        ]

    def _resolve_provider_and_model(
        self, conversation: Conversation, model_id: uuid.UUID | None
    ) -> tuple[AIProvider, AIModel, str | None]:
        resolved_model_id = model_id or conversation.model_id
        if resolved_model_id is None:
            raise AppError("AI_PROVIDER_ERROR", "请先选择模型", status_code=400)
        model = self.db.get(AIModel, resolved_model_id)
        if model is None or not model.enabled:
            raise AppError("AI_PROVIDER_ERROR", "模型不存在或已停用", status_code=400)
        provider_id = conversation.provider_id or model.provider_id
        provider = (
            self.db.execute(
                select(AIProvider).where(
                    AIProvider.id == provider_id, AIProvider.deleted_at.is_(None)
                )
            ).scalar_one_or_none()
            if provider_id is not None
            else None
        )
        if provider is None or not provider.enabled:
            raise AppError("AI_PROVIDER_ERROR", "请先配置并启用 AI 提供商", status_code=400)
        api_key = None
        if provider.encrypted_api_key:
            try:
                api_key = decrypt_text(provider.encrypted_api_key)
            except Exception as exc:  # noqa: BLE001 - 统一错误提示
                raise AppError("AI_PROVIDER_ERROR", "API Key 解密失败", status_code=400) from exc
        return provider, model, api_key

    # ---- 流式对话 ----

    async def stream_send(
        self, conversation_id: uuid.UUID, user_text: str, model_id: uuid.UUID | None = None
    ) -> AsyncIterator[str]:
        db = SessionLocal()
        try:
            conversation = self.get_conversation(conversation_id)
            provider, model, api_key = self._resolve_provider_and_model(conversation, model_id)
            user_msg = ConversationMessage(
                conversation_id=conversation_id,
                role="user",
                content=user_text,
                status="completed",
            )
            db.add(user_msg)
            db.commit()
            assistant = ConversationMessage(
                conversation_id=conversation_id,
                role="assistant",
                content="",
                status="generating",
                generated_by_ai=True,
            )
            db.add(assistant)
            db.commit()
            assistant_id = assistant.id

            context = self._build_context(conversation, user_text)
            adapter = build_provider(provider, api_key)
            request = ChatRequest(model=model.model_id, messages=context)
            cancel_event = _cancel_events[str(conversation_id)]
            cancel_event.clear()
            start = time.monotonic()
            chunks: list[str] = []
            status = "completed"
            error_message: str | None = None
            try:
                async for delta in adapter.stream_chat(request):
                    if cancel_event.is_set():
                        status = "stopped"
                        break
                    chunks.append(delta)
                    yield self._sse({"type": "delta", "content": delta})
            except ProviderError as exc:
                status = "failed"
                error_message = str(exc)
            except Exception:  # noqa: BLE001 - 网络等未知错误
                status = "failed"
                error_message = "对话生成失败，请重试"
            finally:
                content = "".join(chunks)
                latency_ms = int((time.monotonic() - start) * 1000)
                message = db.get(ConversationMessage, assistant_id)
                if message is not None:
                    message.content = content
                    message.status = status
                    message.latency_ms = latency_ms
                db.commit()
                if status == "failed":
                    yield self._sse({"type": "error", "message": error_message or "生成失败"})
                else:
                    yield self._sse(
                        {"type": "done", "message_id": str(assistant_id), "status": status}
                    )
        except AppError as exc:
            yield self._sse({"type": "error", "message": exc.message, "code": exc.code})
        except Exception:  # noqa: BLE001 - 兜底
            yield self._sse({"type": "error", "message": "对话服务异常"})
        finally:
            db.close()

    async def stream_regenerate(
        self, conversation_id: uuid.UUID, message_id: uuid.UUID
    ) -> AsyncIterator[str]:
        db = SessionLocal()
        try:
            conversation = self.get_conversation(conversation_id)
            assistant = db.get(ConversationMessage, message_id)
            if (
                assistant is None
                or assistant.conversation_id != conversation_id
                or not assistant.generated_by_ai
            ):
                yield self._sse({"type": "error", "message": "消息不存在"})
                return
            previous = (
                db.execute(
                    select(ConversationMessage)
                    .where(
                        ConversationMessage.conversation_id == conversation_id,
                        ConversationMessage.created_at < assistant.created_at,
                    )
                    .order_by(ConversationMessage.created_at.desc())
                )
                .scalars()
                .first()
            )
            if previous is None or previous.role != "user":
                yield self._sse({"type": "error", "message": "找不到对应的用户消息"})
                return
            provider, model, api_key = self._resolve_provider_and_model(conversation, None)
            context = self._build_context(conversation, previous.content or "")
            adapter = build_provider(provider, api_key)
            request = ChatRequest(model=model.model_id, messages=context)
            cancel_event = _cancel_events[str(conversation_id)]
            cancel_event.clear()
            start = time.monotonic()
            chunks: list[str] = []
            status = "completed"
            error_message: str | None = None
            assistant.content = ""
            assistant.status = "generating"
            db.commit()
            try:
                async for delta in adapter.stream_chat(request):
                    if cancel_event.is_set():
                        status = "stopped"
                        break
                    chunks.append(delta)
                    yield self._sse({"type": "delta", "content": delta})
            except ProviderError as exc:
                status = "failed"
                error_message = str(exc)
            except Exception:  # noqa: BLE001
                status = "failed"
                error_message = "重新生成失败，请重试"
            finally:
                assistant.content = "".join(chunks)
                assistant.status = status
                assistant.latency_ms = int((time.monotonic() - start) * 1000)
                db.commit()
                if status == "failed":
                    yield self._sse({"type": "error", "message": error_message or "生成失败"})
                else:
                    yield self._sse(
                        {"type": "done", "message_id": str(message_id), "status": status}
                    )
        except AppError as exc:
            yield self._sse({"type": "error", "message": exc.message, "code": exc.code})
        finally:
            db.close()

    @staticmethod
    def cancel(conversation_id: uuid.UUID) -> None:
        _cancel_events[str(conversation_id)].set()

    @staticmethod
    def _sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
