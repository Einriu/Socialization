"""人物时间线 API 测试。"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient


def test_timeline_merges_events_sorted(client: TestClient) -> None:
    person = client.post("/api/persons", json={"name": "时间线主角"}).json()["data"]
    person_id = person["id"]

    client.post(
        f"/api/persons/{person_id}/facts",
        json={"fact_type": "喜好", "content": "喜欢徒步"},
    )
    client.post(
        f"/api/persons/{person_id}/dates",
        json={"title": "生日", "date_value": "2000-01-01"},
    )
    client.post(
        "/api/interactions",
        json={
            "title": "爬山",
            "occurred_at": datetime.now(UTC).isoformat(),
            "participant_ids": [person_id],
        },
    )

    resp = client.get(f"/api/persons/{person_id}/timeline")
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["total"] == 3
    types = [item["type"] for item in body["items"]]
    assert set(types) == {"interaction", "fact", "important_date"}
    occurred = [item["occurred_at"] for item in body["items"]]
    assert occurred == sorted(occurred, reverse=True)


def test_timeline_pagination(client: TestClient) -> None:
    person = client.post("/api/persons", json={"name": "分页主角"}).json()["data"]
    person_id = person["id"]
    for i in range(3):
        client.post(
            "/api/interactions",
            json={"title": f"互动{i}", "participant_ids": [person_id]},
        )
    resp = client.get(f"/api/persons/{person_id}/timeline?page=1&page_size=2")
    body = resp.json()["data"]
    assert body["total"] == 3
    assert len(body["items"]) == 2
