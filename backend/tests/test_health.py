"""GET /api/health 测试。"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["version"] == "0.0.0-test"
    assert data["app_name"] == "Socialization"
    assert data["database"]["connected"] is True
    assert data["database"]["select_1_ok"] is True
    assert data["database"]["journal_mode"] == "wal"
