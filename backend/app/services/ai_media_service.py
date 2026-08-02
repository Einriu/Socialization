"""AI 媒体处理：图片 OCR 与音频转文字（依赖已配置的提供商）。"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.encryption import decrypt_text
from app.models.ai import AIModel, AIProvider
from app.providers.registry import build_provider

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".mp4", ".mkv", ".webm"}


def _find_row(db: Session, model_type: str, vision: bool = False):
    stmt = (
        select(AIModel, AIProvider)
        .join(AIProvider, AIProvider.id == AIModel.provider_id)
        .where(
            AIModel.enabled.is_(True),
            AIProvider.deleted_at.is_(None),
            AIProvider.enabled.is_(True),
            AIProvider.encrypted_api_key.is_not(None),
        )
    )
    if model_type:
        stmt = stmt.where(AIModel.model_type == model_type)
    if vision:
        stmt = stmt.where(AIModel.supports_vision.is_(True))
    return db.execute(stmt).first()


def _adapter_for(row: tuple[AIModel, AIProvider]):
    model, provider = row
    adapter = build_provider(provider, decrypt_text(provider.encrypted_api_key))
    return adapter, model.model_id


def ocr_media(db: Session, file_path: Path) -> str | None:
    """图片 OCR：优先 supports_vision 的模型，失败返回 None。"""
    import asyncio
    import base64

    row = _find_row(db, "chat", vision=True) or _find_row(db, "chat")
    if row is None:
        return None
    try:
        adapter, model_id = _adapter_for(row)
        encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
        return asyncio.get_event_loop().run_until_complete(
            adapter.ocr_image(encoded, model_id)
        )
    except Exception:  # noqa: BLE001 - 媒体处理失败返回 None
        return None


def transcribe_media(db: Session, file_path: Path) -> str | None:
    """音频/视频转文字：调用 /audio/transcriptions。"""
    import asyncio

    row = _find_row(db, "chat")
    if row is None:
        return None
    try:
        adapter, model_id = _adapter_for(row)
        return asyncio.get_event_loop().run_until_complete(
            adapter.transcribe_audio(str(file_path), model_id)
        )
    except Exception:  # noqa: BLE001
        return None
