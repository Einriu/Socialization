"""话题、分类与笔记 API 测试。"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _person(client: TestClient, name: str) -> str:
    return client.post("/api/persons", json={"name": name}).json()["data"]["id"]


def test_category_tree_and_crud(client: TestClient) -> None:
    parent = client.post(
        "/api/topic-categories", json={"name": "科技"}
    ).json()["data"]
    child = client.post(
        "/api/topic-categories", json={"name": "AI", "parent_id": parent["id"]}
    ).json()["data"]
    tree = client.get("/api/topic-categories").json()["data"]
    assert tree[0]["name"] == "科技"
    assert tree[0]["children"][0]["name"] == "AI"

    # 循环层级被拒绝
    resp = client.patch(
        f"/api/topic-categories/{parent['id']}", json={"parent_id": child["id"]}
    )
    assert resp.status_code == 409

    # 有子分类时删除被拒绝
    assert client.delete(f"/api/topic-categories/{parent['id']}").status_code == 409
    assert client.delete(f"/api/topic-categories/{child['id']}").status_code == 204
    assert client.delete(f"/api/topic-categories/{parent['id']}").status_code == 204


def test_topic_crud_and_filter(client: TestClient) -> None:
    category = client.post(
        "/api/topic-categories", json={"name": "美食"}
    ).json()["data"]
    created = client.post(
        "/api/topics",
        json={"name": "咖啡", "category_id": category["id"], "mastery_level": 2},
    ).json()["data"]
    assert created["name"] == "咖啡"
    assert created["mastery_level"] == 2

    resp = client.get(f"/api/topics?category_id={category['id']}")
    assert resp.json()["data"]["total"] == 1
    resp = client.get("/api/topics?q=咖啡")
    assert resp.json()["data"]["total"] == 1

    resp = client.patch(f"/api/topics/{created['id']}", json={"mastery_level": 4})
    assert resp.json()["data"]["mastery_level"] == 4
    assert client.delete(f"/api/topics/{created['id']}").status_code == 204


def test_topic_person_links(client: TestClient) -> None:
    person_id = _person(client, "咖啡同好")
    topic = client.post("/api/topics", json={"name": "手冲咖啡"}).json()["data"]
    resp = client.put(
        f"/api/topics/{topic['id']}/persons", json={"person_ids": [person_id]}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["persons"][0]["name"] == "咖啡同好"


def test_note_save_get_and_concurrency(client: TestClient) -> None:
    topic = client.post("/api/topics", json={"name": "旅行"}).json()["data"]
    topic_id = topic["id"]
    first = client.put(
        f"/api/topics/{topic_id}/notes",
        json={"content_json": {"type": "doc", "content": []}, "plain_text": "首版笔记"},
    ).json()["data"]
    assert first["plain_text"] == "首版笔记"

    second = client.put(
        f"/api/topics/{topic_id}/notes",
        json={
            "content_json": {"type": "doc", "content": []},
            "plain_text": "第二版",
            "expected_updated_at": first["updated_at"],
        },
    )
    assert second.status_code == 200

    stale = client.put(
        f"/api/topics/{topic_id}/notes",
        json={
            "content_json": {"type": "doc", "content": []},
            "plain_text": "过期版本",
            "expected_updated_at": first["updated_at"],
        },
    )
    assert stale.status_code == 409

    got = client.get(f"/api/topics/{topic_id}/notes").json()["data"]
    assert got["plain_text"] == "第二版"
