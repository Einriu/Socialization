"""AI 提供商与模型管理业务逻辑。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.encryption import decrypt_text, encrypt_text
from app.core.exceptions import AppError
from app.models.ai import AIModel, AIProvider
from app.providers.base import ProviderError
from app.providers.registry import build_provider
from app.repositories.base import BaseRepository
from app.schemas.provider import ModelCreate, ModelUpdate, ProviderCreate, ProviderUpdate


class ProviderRepository(BaseRepository[AIProvider]):
    model = AIProvider


class ModelRepository(BaseRepository[AIModel]):
    model = AIModel


def _mask(api_key: str | None) -> tuple[bool, str | None]:
    if not api_key:
        return False, None
    return True, api_key[-4:]


class ProviderService:
    """提供商与模型服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.providers = ProviderRepository(db)
        self.models = ModelRepository(db)

    def _get_provider(self, provider_id: uuid.UUID) -> AIProvider:
        provider = self.db.execute(
            select(AIProvider).where(
                AIProvider.id == provider_id, AIProvider.deleted_at.is_(None)
            )
        ).scalar_one_or_none()
        if provider is None:
            raise AppError("NOT_FOUND", status_code=404)
        return provider

    def _decrypt_key(self, provider: AIProvider) -> str | None:
        if not provider.encrypted_api_key:
            return None
        try:
            return decrypt_text(provider.encrypted_api_key)
        except Exception as exc:  # noqa: BLE001 - 解密失败统一提示
            raise AppError("AI_PROVIDER_ERROR", "API Key 解密失败", status_code=400) from exc

    def list_providers(self, page: int, page_size: int) -> tuple[list[AIProvider], int]:
        stmt = select(AIProvider).where(AIProvider.deleted_at.is_(None))
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(AIProvider.created_at.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_provider(self, provider_id: uuid.UUID) -> AIProvider:
        return self._get_provider(provider_id)

    def create_provider(self, data: ProviderCreate) -> AIProvider:
        payload = data.model_dump(exclude={"api_key"})
        encrypted = encrypt_text(data.api_key) if data.api_key else None
        return self.providers.create(AIProvider(**payload, encrypted_api_key=encrypted))

    def update_provider(self, provider_id: uuid.UUID, data: ProviderUpdate) -> AIProvider:
        provider = self._get_provider(provider_id)
        values = data.model_dump(exclude={"api_key", "clear_api_key"})
        if data.clear_api_key:
            provider.encrypted_api_key = None
        if data.api_key:
            provider.encrypted_api_key = encrypt_text(data.api_key)
        for key, value in values.items():
            if value is not None or key == "base_url":
                setattr(provider, key, value)
        self.db.flush()
        return provider

    def delete_provider(self, provider_id: uuid.UUID) -> None:
        if not self.providers.soft_delete(provider_id):
            raise AppError("NOT_FOUND", status_code=404)

    async def test_provider(self, provider_id: uuid.UUID) -> dict:
        provider = self._get_provider(provider_id)
        adapter = build_provider(provider, self._decrypt_key(provider))
        try:
            result = await adapter.test_connection()
        except ProviderError as exc:
            raise AppError("AI_PROVIDER_ERROR", str(exc), status_code=400) from exc
        provider.last_tested_at = time_utcnow()
        self.db.flush()
        return result

    def list_models(self, provider_id: uuid.UUID) -> list[AIModel]:
        self._get_provider(provider_id)
        return list(
            self.db.execute(
                select(AIModel)
                .where(AIModel.provider_id == provider_id)
                .order_by(AIModel.created_at.asc())
            ).scalars()
        )

    async def sync_models(self, provider_id: uuid.UUID) -> dict:
        provider = self._get_provider(provider_id)
        adapter = build_provider(provider, self._decrypt_key(provider))
        try:
            remote = await adapter.list_models()
        except ProviderError as exc:
            raise AppError("AI_PROVIDER_ERROR", str(exc), status_code=400) from exc
        created = 0
        updated = 0
        for item in remote:
            model_id = item.get("model_id", "")
            if not model_id:
                continue
            existing = self.db.execute(
                select(AIModel).where(
                    AIModel.provider_id == provider_id, AIModel.model_id == model_id
                )
            ).scalar_one_or_none()
            if existing is None:
                self.db.add(
                    AIModel(
                        provider_id=provider_id,
                        model_id=model_id,
                        display_name=item.get("display_name") or model_id,
                        source="sync",
                    )
                )
                created += 1
            elif existing.source != "manual":
                existing.display_name = item.get("display_name") or model_id
                updated += 1
        self.db.flush()
        return {"created": created, "updated": updated}

    def create_model(self, provider_id: uuid.UUID, data: ModelCreate) -> AIModel:
        self._get_provider(provider_id)
        duplicate = self.db.execute(
            select(AIModel).where(
                AIModel.provider_id == provider_id, AIModel.model_id == data.model_id
            )
        ).scalar_one_or_none()
        if duplicate is not None:
            raise AppError("CONFLICT", "该模型已存在", status_code=409)
        return self.models.create(AIModel(provider_id=provider_id, **data.model_dump()))

    def update_model(self, model_id: uuid.UUID, data: ModelUpdate) -> AIModel:
        model = self.models.update(model_id, data.model_dump(exclude_unset=True))
        if model is None:
            raise AppError("NOT_FOUND", status_code=404)
        return model

    def delete_model(self, model_id: uuid.UUID) -> None:
        if not self.models.hard_delete(model_id):
            raise AppError("NOT_FOUND", status_code=404)
def time_utcnow() -> datetime:
    """返回当前 UTC 时间（供 last_tested_at 使用）。"""
    return datetime.now(UTC)
