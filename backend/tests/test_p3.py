"""P3 增强版本测试：人物关系、网页收藏、Ollama 预设、AI 媒体处理。"""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models.ai import AIProvider
from app.providers.registry import build_provider
from app.services.ai_media_service import ocr_media, transcribe_media


def test_relationships_crud(client: TestClient) -> None:
    p1 = client.post("/api/persons", json={"name": "关系甲"}).json()["data"]
    p2 = client.post("/api/persons", json={"name": "关系乙"}).json()["data"]
    resp = client.post(
        f"/api/persons/{p1['id']}/relationships",
        json={"other_person_id": p2["id"], "relation_type": "同事"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["other_person_name"] == "关系乙"

    relations = client.get(f"/api/persons/{p1['id']}/relationships").json()["data"]
    assert len(relations) == 1
    # 对称可见
    assert len(client.get(f"/api/persons/{p2['id']}/relationships").json()["data"]) == 1
    # 重复关系被拒绝
    dup = client.post(
        f"/api/persons/{p1['id']}/relationships",
        json={"other_person_id": p2["id"], "relation_type": "朋友"},
    )
    assert dup.status_code == 409
    assert client.delete(f"/api/relationships/{relations[0]['id']}").status_code == 200


def test_web_clip_saves_document(client: TestClient, monkeypatch: object) -> None:
    class FakeResponse:
        text = "<html><body><h1>收藏标题</h1><p>收藏的正文内容</p></body></html>"

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "app.api.web_clips.httpx.get",
        lambda *args, **kwargs: FakeResponse(),
    )
    resp = client.post(
        "/api/web-clips", json={"url": "https://example.com/article", "title": "示例文章"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "completed"
    assert data["filename"].startswith("示例文章")


def test_ollama_provider_preset(client: TestClient) -> None:
        provider = client.post(
            "/api/providers", json={"name": "本地模型", "provider_type": "ollama"}
        ).json()["data"]
        assert provider["provider_type"] == "ollama"
        with SessionLocal() as db:
            row = db.get(AIProvider, uuid.UUID(provider["id"]))
        adapter = build_provider(row, None)
        assert adapter.base_url == "http://127.0.0.1:11434/v1"


def test_ai_media_ocr_and_transcribe(client: TestClient, monkeypatch: object) -> None:
    class FakeMediaAdapter:
        def __init__(self) -> None:
            self.ocr_called = False
            self.transcribe_called = False

        async def ocr_image(self, image_base64: str, model: str) -> str:
            self.ocr_called = True
            return "识别出的文字"

        async def transcribe_audio(self, file_path: str, model: str) -> str:
            self.transcribe_called = True
            return "转写出的文字"

    fake = FakeMediaAdapter()
    monkeypatch.setattr(
        "app.services.ai_media_service.build_provider",
        lambda provider, api_key: fake,
    )
    provider = client.post(
        "/api/providers",
        json={"name": "媒体提供商", "provider_type": "openai_compatible", "api_key": "sk-x"},
    ).json()["data"]
    client.post(
        f"/api/providers/{provider['id']}/models",
        json={"model_id": "vision-model", "supports_vision": True},
    )
    with SessionLocal() as db:
        tmp = Path(tempfile.gettempdir()) / "socialization-media-test.png"
        tmp.write_bytes(b"fake-image-bytes")
        ocr_result = ocr_media(db, tmp)
        assert ocr_result == "识别出的文字"
        assert fake.ocr_called
        transcribe_result = transcribe_media(db, tmp)
        assert transcribe_result == "转写出的文字"
        assert fake.transcribe_called
        tmp.unlink(missing_ok=True)
