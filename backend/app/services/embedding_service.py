"""嵌入生成（可选）：找到可用的嵌入模型并调用提供商。"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.encryption import decrypt_text
from app.models.ai import AIModel, AIProvider
from app.providers.registry import build_provider


def embed_texts(db: Session, texts: list[str]) -> list[list[float]] | None:
    """对文本生成向量；未配置嵌入模型或失败时返回 None（降级为关键词检索）。"""
    if not texts:
        return None
    model = (
        db.execute(
            select(AIModel)
            .join(AIProvider, AIProvider.id == AIModel.provider_id)
            .where(
                AIModel.model_type == "embedding",
                AIModel.enabled.is_(True),
                AIProvider.deleted_at.is_(None),
                AIProvider.enabled.is_(True),
                AIProvider.encrypted_api_key.is_not(None),
            )
        )
        .scalars()
        .first()
    )
    if model is None:
        return None
    provider = db.get(AIProvider, model.provider_id)
    if provider is None:
        return None
    try:
        adapter = build_provider(provider, decrypt_text(provider.encrypted_api_key))
        return asyncio.get_event_loop().run_until_complete(
            adapter.create_embeddings(model.model_id, texts)
        )
    except Exception:  # noqa: BLE001 - 嵌入失败时降级
        return None
