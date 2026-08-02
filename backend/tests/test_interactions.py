"""互动记录 API 测试。"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _person(client: TestClient, name: str) -> dict:
    return client.post("/api/persons", json={"name": name}).json()["data"]


def test_create_interaction_with_participants_and_follow_up(client: TestClient) -> None:
    p1 = _person(client, "甲方")
    p2 = _person(client, "乙方")
    resp = client.post(
        "/api/interactions",
        json={
            "title": "一起喝咖啡",
            "interaction_type": "meal",
            "duration_minutes": 60,
            "summary": "聊了最近工作",
            "follow_up": "下周跟进项目进展",
            "participant_ids": [p1["id"], p2["id"]],
        },
    )
    assert resp.status_code == 200
    item = resp.json()["data"]
    assert {p["name"] for p in item["persons"]} == {"甲方", "乙方"}
    assert item["interaction_type"] == "meal"

    follow_ups = client.get(f"/api/persons/{p1['id']}/follow-ups").json()["data"]
    assert follow_ups["total"] == 1
    assert follow_ups["items"][0]["title"] == "下周跟进项目进展"
    assert follow_ups["items"][0]["interaction_id"] == item["id"]


def test_interaction_requires_participants(client: TestClient) -> None:
    resp = client.post("/api/interactions", json={"title": "无参与者互动"})
    assert resp.status_code == 422


def test_interaction_list_filter_by_person(client: TestClient) -> None:
    p1 = _person(client, "筛选甲")
    p2 = _person(client, "筛选乙")
    client.post(
        "/api/interactions",
        json={"title": "与甲互动", "participant_ids": [p1["id"]]},
    )
    client.post(
        "/api/interactions",
        json={"title": "与乙互动", "participant_ids": [p2["id"]]},
    )
    resp = client.get(f"/api/interactions?person_id={p1['id']}")
    body = resp.json()["data"]
    assert body["total"] == 1
    assert body["items"][0]["title"] == "与甲互动"


def test_interaction_update_and_delete(client: TestClient) -> None:
    p1 = _person(client, "更新甲")
    p2 = _person(client, "更新乙")
    created = client.post(
        "/api/interactions",
        json={"title": "初始标题", "participant_ids": [p1["id"]]},
    ).json()["data"]
    interaction_id = created["id"]

    resp = client.patch(
        f"/api/interactions/{interaction_id}",
        json={"title": "新标题", "participant_ids": [p2["id"]]},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == "新标题"
    assert {p["name"] for p in data["persons"]} == {"更新乙"}

    assert client.delete(f"/api/interactions/{interaction_id}").status_code == 204
    assert client.get(f"/api/interactions/{interaction_id}").status_code == 404


def test_missing_participant_returns_404(client: TestClient) -> None:
    resp = client.post(
        "/api/interactions",
        json={"title": "无效人物", "participant_ids": [str(uuid.uuid4())]},
    )
    assert resp.status_code == 404
