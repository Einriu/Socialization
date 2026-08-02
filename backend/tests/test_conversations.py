"""AI 会话、上下文隔离与 SSE 流式对话测试。"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.providers.base import ProviderError
from app.services import conversation_service


class FakeProvider:
    """假提供商：可配置输出块或抛错，并记录最后一次请求。"""

    def __init__(self, chunks: list[str] | None = None, error: str | None = None) -> None:
        self.chunks = chunks or ["你好", "，", "世界"]
        self.error = error
        self.last_request = None

    async def stream_chat(self, request: object) -> object:
        self.last_request = request
        if self.error:
            raise ProviderError(self.error)
        for chunk in self.chunks:
            yield chunk


def _create_conversation(client: TestClient) -> str:
    resp = client.post("/api/conversations", json={"title": "测试对话"})
    assert resp.status_code == 200
    return resp.json()["data"]["id"]


def _prepare_chat_env(client: TestClient, monkeypatch: object) -> tuple[str, FakeProvider]:
    provider_row = client.post(
        "/api/providers",
        json={"name": "对话提供商", "provider_type": "openai_compatible", "api_key": "sk-x"},
    ).json()["data"]
    model = client.post(
        f"/api/providers/{provider_row['id']}/models",
        json={"model_id": "chat-model"},
    ).json()["data"]
    conversation_id = _create_conversation(client)
    client.patch(
        f"/api/conversations/{conversation_id}",
        json={"provider_id": provider_row["id"], "model_id": model["id"]},
    )
    fake = FakeProvider()
    monkeypatch.setattr(
        "app.services.conversation_service.build_provider",
        lambda provider, api_key: fake,
    )
    return conversation_id, fake


def test_conversation_crud_and_links(client: TestClient) -> None:
    conversation_id = _create_conversation(client)
    person = client.post("/api/persons", json={"name": "对话关联人"}).json()["data"]
    topic = client.post("/api/topics", json={"name": "对话关联话题"}).json()["data"]

    resp = client.put(
        f"/api/conversations/{conversation_id}/links",
        json={"person_id": person["id"], "topic_id": topic["id"]},
    )
    assert resp.status_code == 200
    links = client.get(f"/api/conversations/{conversation_id}/links").json()["data"]
    assert len(links) == 2

    resp = client.patch(f"/api/conversations/{conversation_id}", json={"title": "改名"})
    assert resp.json()["data"]["title"] == "改名"


def test_context_isolation_and_sses_stream(
    client: TestClient, monkeypatch: object
) -> None:
    conversation_id, fake = _prepare_chat_env(client, monkeypatch)
    person_a = client.post("/api/persons", json={"name": "甲"}).json()["data"]
    person_b = client.post("/api/persons", json={"name": "乙"}).json()["data"]
    client.post(
        f"/api/persons/{person_a['id']}/facts",
        json={"fact_type": "喜好", "content": "喜欢咖啡"},
    )
    client.post(
        f"/api/persons/{person_a['id']}/facts",
        json={
            "fact_type": "禁忌",
            "content": "过敏秘密",
            "is_sensitive": True,
        },
    )
    client.post(
        f"/api/persons/{person_b['id']}/facts",
        json={"fact_type": "喜好", "content": "乙的私人兴趣"},
    )
    client.put(
        f"/api/conversations/{conversation_id}/links",
        json={"person_id": person_a["id"]},
    )

    resp = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"content": "今天聊什么？"},
    )
    assert resp.status_code == 200
    body = "".join(resp.iter_text())
    assert '"type": "delta"' in body
    assert '"type": "done"' in body

    system_content = fake.last_request.messages[0].content
    assert "喜欢咖啡" in system_content
    assert "过敏秘密" not in system_content
    assert "乙的私人兴趣" not in system_content

    messages = client.get(
        f"/api/conversations/{conversation_id}/messages"
    ).json()["data"]
    assert messages["total"] == 2
    roles = [item["role"] for item in messages["items"]]
    assert roles == ["user", "assistant"]
    assistant = messages["items"][1]
    assert assistant["generated_by_ai"] is True
    assert assistant["status"] == "completed"
    assert assistant["content"] == "你好，世界"


def test_failure_keeps_user_message(client: TestClient, monkeypatch: object) -> None:
    conversation_id, _ = _prepare_chat_env(client, monkeypatch)
    fake = FakeProvider(error="网络不可达")
    monkeypatch.setattr(
        "app.services.conversation_service.build_provider",
        lambda provider, api_key: fake,
    )
    resp = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"content": "这条消息应保留"},
    )
    body = "".join(resp.iter_text())
    assert '"type": "error"' in body
    messages = client.get(
        f"/api/conversations/{conversation_id}/messages"
    ).json()["data"]
    assert messages["total"] == 2
    assert messages["items"][0]["content"] == "这条消息应保留"
    assert messages["items"][1]["status"] == "failed"


def test_regenerate_replaces_content(client: TestClient, monkeypatch: object) -> None:
    conversation_id, _ = _prepare_chat_env(client, monkeypatch)
    fake = FakeProvider(chunks=["第一版回答"])
    monkeypatch.setattr(
        "app.services.conversation_service.build_provider",
        lambda provider, api_key: fake,
    )
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"content": "问题"},
    )
    messages = client.get(
        f"/api/conversations/{conversation_id}/messages"
    ).json()["data"]
    assistant_id = messages["items"][1]["id"]

    fake.chunks = ["第二版回答"]
    resp = client.post(
        f"/api/conversations/{conversation_id}/messages/{assistant_id}/regenerate"
    )
    body = "".join(resp.iter_text())
    assert '"type": "done"' in body
    messages = client.get(
        f"/api/conversations/{conversation_id}/messages"
    ).json()["data"]
    assert messages["total"] == 2
    assert messages["items"][1]["content"] == "第二版回答"


def test_cancel_sets_event(client: TestClient) -> None:
    conversation_id = _create_conversation(client)
    resp = client.post(f"/api/conversations/{conversation_id}/cancel")
    assert resp.status_code == 200
    assert conversation_service._cancel_events[str(conversation_id)].is_set()
