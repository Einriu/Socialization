"""AI 提供商与模型管理测试。"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models.ai import AIProvider


class FakeAdapter:
    """用于测试的假适配器。"""

    def __init__(self, models: list[dict] | None = None) -> None:
        self.models = models or [
            {"model_id": "deepseek-chat", "display_name": "DeepSeek Chat"}
        ]

    async def test_connection(self) -> dict:
        return {"ok": True, "models": len(self.models), "latency_ms": 12}

    async def list_models(self) -> list[dict]:
        return self.models


def _create_provider(client: TestClient, api_key: str = "sk-plaintext-1234") -> dict:
    resp = client.post(
        "/api/providers",
        json={
            "name": "测试提供商",
            "provider_type": "deepseek",
            "api_key": api_key,
        },
    )
    assert resp.status_code == 200
    return resp.json()["data"]


def test_provider_crud_with_encrypted_key(client: TestClient) -> None:
    provider = _create_provider(client)
    assert provider["has_api_key"] is True
    assert provider["key_hint"] == "1234"
    assert "api_key" not in provider
    assert provider["provider_type"] == "deepseek"

    with SessionLocal() as db:
        row = db.get(AIProvider, uuid.UUID(provider["id"]))
        assert row is not None
        assert row.encrypted_api_key is not None
        assert "sk-plaintext-1234" not in row.encrypted_api_key

    resp = client.patch(
        f"/api/providers/{provider['id']}", json={"clear_api_key": True}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["has_api_key"] is False
    assert client.delete(f"/api/providers/{provider['id']}").status_code == 204


def test_test_connection_and_sync_models(
    client: TestClient, monkeypatch: object
) -> None:
    fake = FakeAdapter()
    monkeypatch.setattr(
        "app.services.provider_service.build_provider",
        lambda provider, api_key: fake,
    )
    provider = _create_provider(client)

    resp = client.post(f"/api/providers/{provider['id']}/test")
    assert resp.status_code == 200
    assert resp.json()["data"]["ok"] is True

    resp = client.post(f"/api/providers/{provider['id']}/sync-models")
    assert resp.status_code == 200
    assert resp.json()["data"]["created"] == 1

    models = client.get(f"/api/providers/{provider['id']}/models").json()["data"]
    assert models[0]["model_id"] == "deepseek-chat"
    assert models[0]["source"] == "sync"


def test_manual_model_and_conflict(client: TestClient) -> None:
    provider = _create_provider(client)
    resp = client.post(
        f"/api/providers/{provider['id']}/models",
        json={"model_id": "my-model", "display_name": "我的模型"},
    )
    assert resp.status_code == 200
    model = resp.json()["data"]
    assert model["source"] == "manual"

    dup = client.post(
        f"/api/providers/{provider['id']}/models", json={"model_id": "my-model"}
    )
    assert dup.status_code == 409

    resp = client.patch(f"/api/ai-models/{model['id']}", json={"enabled": False})
    assert resp.json()["data"]["enabled"] is False
