"""标签 API 测试。"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_tag_crud(client: TestClient) -> None:
    resp = client.post("/api/tags", json={"name": "朋友", "color": "#00ff00", "group_name": "关系"})
    assert resp.status_code == 200
    tag = resp.json()["data"]
    assert tag["name"] == "朋友"

    resp = client.patch(f"/api/tags/{tag['id']}", json={"color": "#0000ff"})
    assert resp.json()["data"]["color"] == "#0000ff"

    resp = client.get("/api/tags")
    assert resp.json()["data"]["total"] >= 1
    assert client.delete(f"/api/tags/{tag['id']}").status_code == 204


def test_tag_name_conflict(client: TestClient) -> None:
    client.post("/api/tags", json={"name": "唯一标签"})
    resp = client.post("/api/tags", json={"name": "唯一标签"})
    assert resp.status_code == 409
    assert resp.json()["code"] == "CONFLICT"


def test_delete_tag_removes_associations(client: TestClient) -> None:
    person_resp = client.post("/api/persons", json={"name": "带标签的人"})
    person_id = person_resp.json()["data"]["id"]
    tag_resp = client.post("/api/tags", json={"name": "待删标签"})
    tag_id = tag_resp.json()["data"]["id"]
    client.put(f"/api/persons/{person_id}/tags", json={"tag_ids": [tag_id]})

    assert client.delete(f"/api/tags/{tag_id}").status_code == 204
    resp = client.get(f"/api/persons/{person_id}")
    assert resp.json()["data"]["tags"] == []
