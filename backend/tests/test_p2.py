"""P2 社交能力测试：简报、提取确认、复盘、练习、复习、记忆。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models.p2 import PracticeScenario, ReviewTask
from app.providers.base import ChatResponse


class FakeChat:
    """假聊天提供商。"""

    def __init__(
        self,
        text: str = "模拟回复",
        stream_chunks: list[str] | None = None,
    ) -> None:
        self.text = text
        self.stream_chunks = stream_chunks or ["你好", "，", "继续"]

    async def chat(self, request: object) -> ChatResponse:
        return ChatResponse(content=self.text)

    async def stream_chat(self, request: object) -> object:
        for chunk in self.stream_chunks:
            yield chunk


def _patch_chat(monkeypatch: object, fake: FakeChat) -> None:
    monkeypatch.setattr(
        "app.services.social_service._resolve_chat", lambda db: (fake, "model")
    )
    monkeypatch.setattr(
        "app.services.practice_service._resolve_chat", lambda db: (fake, "model")
    )


def test_briefing_generates_text(client: TestClient, monkeypatch: object) -> None:
    fake = FakeChat(text="开场：聊聊最近的周末安排。")
    _patch_chat(monkeypatch, fake)
    person = client.post("/api/persons", json={"name": "简报人"}).json()["data"]
    resp = client.post(f"/api/persons/{person['id']}/briefing")
    assert resp.status_code == 200
    assert "开场" in resp.json()["data"]["briefing"]


def test_extract_confirm_and_review(client: TestClient, monkeypatch: object) -> None:
    fake = FakeChat(
        text='[{"kind":"fact","fact_type":"喜好","content":"喜欢跑步"},'
        '{"kind":"follow_up","fact_type":"","content":"下周约跑步"}]'
    )
    _patch_chat(monkeypatch, fake)
    person = client.post("/api/persons", json={"name": "提取人"}).json()["data"]
    interaction = client.post(
        "/api/interactions",
        json={"title": "跑步聊天", "participant_ids": [person["id"]]},
    ).json()["data"]

    extracted = client.post(
        f"/api/interactions/{interaction['id']}/extract"
    ).json()["data"]
    assert len(extracted) == 2
    ids = [item["id"] for item in extracted]
    pending = client.get(
        f"/api/interactions/{interaction['id']}/extractions"
    ).json()["data"]
    assert len(pending) == 2

    confirmed = client.post(
        f"/api/interactions/{interaction['id']}/confirm-extractions",
        json={"ids": ids},
    ).json()["data"]
    assert confirmed["confirmed"] == 2

    facts = client.get(f"/api/persons/{person['id']}/facts").json()["data"]
    assert any(item["content"] == "喜欢跑步" for item in facts["items"])
    followups = client.get(f"/api/persons/{person['id']}/follow-ups").json()["data"]
    assert followups["total"] == 1

    fake.text = "复盘：倾听很好，可多追问细节。"
    review = client.post(
        f"/api/interactions/{interaction['id']}/review"
    ).json()["data"]
    assert "追问" in review["review"]


def test_practice_stream_and_evaluate(
    client: TestClient, monkeypatch: object
) -> None:
    fake = FakeChat(
        text='{"scores":{"倾听能力":8,"共情表达":7,"多角色参与":9},"summary":"整体不错"}',
        stream_chunks=["【张三】今天天气不错。\n", "【李四】是啊，", "适合出去走走。"],
    )
    _patch_chat(monkeypatch, fake)
    with SessionLocal() as db:
        scenario = PracticeScenario(
            scenario_type="stranger",
            title="陌生人初次交流",
            description="测试场景",
        )
        db.add(scenario)
        db.commit()
        scenario_id = str(scenario.id)

    session = client.post(
        "/api/practice/sessions", json={"scenario_id": scenario_id}
    ).json()["data"]
    resp = client.post(
        f"/api/practice/sessions/{session['id']}/messages",
        json={"content": "你好，我叫小张"},
    )
    body = "".join(resp.iter_text())
    assert '"type": "done"' in body
    messages = client.get(
        f"/api/practice/sessions/{session['id']}/messages"
    ).json()["data"]
    assert len(messages) == 2
    assert "【张三】" in messages[1]["content"]
    assert "【李四】" in messages[1]["content"]
    assert messages[1]["content"] == "【张三】今天天气不错。\n【李四】是啊，适合出去走走。"

    evaluation = client.post(
        f"/api/practice/sessions/{session['id']}/evaluate"
    ).json()["data"]
    assert evaluation["scores"]["倾听能力"] == 8
    assert evaluation["scores"]["多角色参与"] == 9
    sessions = client.get("/api/practice/sessions").json()["data"]
    assert sessions[0]["status"] == "completed"


def test_review_answer_schedules_next(client: TestClient) -> None:
    topic = client.post("/api/topics", json={"name": "复习话题"}).json()["data"]
    with SessionLocal() as db:
        task = ReviewTask(
            topic_id=uuid.UUID(topic["id"]),
            due_at=datetime.now(UTC) - timedelta(hours=1),
            interval_days=1,
        )
        db.add(task)
        db.commit()
        task_id = str(task.id)
    resp = client.post(f"/api/reviews/{task_id}/answer?rating=掌握")
    assert resp.status_code == 200
    assert resp.json()["data"]["interval_days"] == 7
    due = client.get("/api/reviews/due").json()["data"]
    assert all(item["id"] != task_id for item in due)


def test_memory_and_dashboard(client: TestClient, monkeypatch: object) -> None:
    fake = FakeChat(text="本周周报内容")
    _patch_chat(monkeypatch, fake)
    client.post("/api/persons", json={"name": "统计人"})
    memory = client.post(
        "/api/memory", json={"kind": "preference", "content": "希望减少连续讲述"}
    ).json()["data"]
    client.patch(f"/api/memory/{memory['id']}", json={"status": "accepted"})
    dashboard = client.get("/api/dashboard").json()["data"]
    assert dashboard["persons"] >= 1
    report = client.post("/api/reports/weekly").json()["data"]
    assert report["report"] == "本周周报内容"
