"""AI 提供商与模型 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.encryption import decrypt_text
from app.core.response import success_response
from app.models.ai import AIProvider
from app.schemas.common import Page
from app.schemas.provider import (
    ModelCreate,
    ModelRead,
    ModelUpdate,
    ProviderCreate,
    ProviderRead,
    ProviderUpdate,
)
from app.services.provider_service import ProviderService

router = APIRouter()


def _provider_read(provider: AIProvider) -> ProviderRead:
    data = ProviderRead.model_validate(provider)
    has_api_key = provider.encrypted_api_key is not None
    key_hint: str | None = None
    if has_api_key:
        try:
            key_hint = decrypt_text(provider.encrypted_api_key)[-4:]
        except Exception:  # noqa: BLE001 - 解密失败时不暴露原因
            key_hint = None
    return data.model_copy(update={"has_api_key": has_api_key, "key_hint": key_hint})


@router.get("/providers")
def list_providers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, total = ProviderService(db).list_providers(page, page_size)
    payload = Page[ProviderRead](
        items=[_provider_read(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/providers")
def create_provider(data: ProviderCreate, db: Session = Depends(get_db)) -> dict:
    item = ProviderService(db).create_provider(data)
    return success_response(_provider_read(item))


@router.get("/providers/{provider_id}")
def get_provider(provider_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    item = ProviderService(db).get_provider(provider_id)
    return success_response(_provider_read(item))


@router.patch("/providers/{provider_id}")
def update_provider(
    provider_id: uuid.UUID, data: ProviderUpdate, db: Session = Depends(get_db)
) -> dict:
    item = ProviderService(db).update_provider(provider_id, data)
    return success_response(_provider_read(item))


@router.delete("/providers/{provider_id}")
def delete_provider(provider_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    ProviderService(db).delete_provider(provider_id)
    return Response(status_code=204)


@router.post("/providers/{provider_id}/test")
async def test_provider(provider_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    result = await ProviderService(db).test_provider(provider_id)
    return success_response(result)


@router.post("/providers/{provider_id}/sync-models")
async def sync_models(provider_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    result = await ProviderService(db).sync_models(provider_id)
    return success_response(result)


@router.get("/providers/{provider_id}/models")
def list_models(provider_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    items = ProviderService(db).list_models(provider_id)
    return success_response([ModelRead.model_validate(item) for item in items])


@router.post("/providers/{provider_id}/models")
def create_model(
    provider_id: uuid.UUID, data: ModelCreate, db: Session = Depends(get_db)
) -> dict:
    item = ProviderService(db).create_model(provider_id, data)
    return success_response(ModelRead.model_validate(item))


@router.patch("/ai-models/{model_id}")
def update_model(
    model_id: uuid.UUID, data: ModelUpdate, db: Session = Depends(get_db)
) -> dict:
    item = ProviderService(db).update_model(model_id, data)
    return success_response(ModelRead.model_validate(item))


@router.delete("/ai-models/{model_id}")
def delete_model(model_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    ProviderService(db).delete_model(model_id)
    return Response(status_code=204)
