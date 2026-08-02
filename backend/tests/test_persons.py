"""人物、标签、事实、日期、跟进与时间线 API 测试。"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models.support import AuditLog


def _create_person(client: TestClient, name: str = "张三") -> dict:
    resp = client.post(
        "/api/persons",
        json={"name": name, "nickname": "三哥", "familiarity_level": 2},
    )
    assert resp.status_code == 200
    return resp.json()["data"]


def _create_tag(client: TestClient, name: str = "同事") -> dict:
    resp = client.post("/api/tags", json={"name": name, "color": "#ff0000"})
    assert resp.status_code == 200
    return resp.json()["data"]


def test_create_and_get_person(client: TestClient) -> None:
    person = _create_person(client)
    person_id = person["id"]
    resp = client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "张三"
    assert data["familiarity_level"] == 2
    assert data["privacy_level"] == "private"


def test_list_persons_pagination_and_search(client: TestClient) -> None:
    _create_person(client, "李明")
    _create_person(client, "王芳")
    resp = client.get("/api/persons?page=1&page_size=1")
    body = resp.json()["data"]
    assert body["total"] == 2
    assert len(body["items"]) == 1
    assert body["page"] == 1

    resp = client.get("/api/persons?q=李明")
    body = resp.json()["data"]
    assert body["total"] == 1
    assert body["items"][0]["name"] == "李明"


def test_update_person(client: TestClient) -> None:
    person = _create_person(client)
    resp = client.patch(
        f"/api/persons/{person['id']}",
        json={"organization": "某公司", "summary": "更新后的摘要"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["organization"] == "某公司"


def test_soft_delete_and_permanent_delete(client: TestClient) -> None:
    person = _create_person(client)
    resp = client.delete(f"/api/persons/{person['id']}")
    assert resp.status_code == 204
    assert client.get(f"/api/persons/{person['id']}").status_code == 404

    person2 = _create_person(client, "赵六")
    resp = client.delete(f"/api/persons/{person2['id']}/permanent")
    assert resp.status_code == 400
    resp = client.delete(f"/api/persons/{person2['id']}/permanent?confirm=true")
    assert resp.status_code == 204
    assert client.get(f"/api/persons/{person2['id']}").status_code == 404


def test_permanent_delete_cleans_associations(client: TestClient) -> None:
    person = _create_person(client, "有关联的人")
    tag = _create_tag(client, "待清标签")
    client.put(f"/api/persons/{person['id']}/tags", json={"tag_ids": [tag["id"]]})
    client.post(
        f"/api/persons/{person['id']}/facts",
        json={"fact_type": "喜好", "content": "喜欢游泳"},
    )
    client.post(
        "/api/interactions",
        json={"title": "游泳", "participant_ids": [person["id"]]},
    )
    resp = client.delete(f"/api/persons/{person['id']}/permanent?confirm=true")
    assert resp.status_code == 204
    assert client.get(f"/api/persons/{person['id']}").status_code == 404
    resp = client.get("/api/tags")
    names = [item["name"] for item in resp.json()["data"]["items"]]
    # 人物被彻底删除；标签是全局实体，应保留
    assert "待清标签" in names


def test_person_tags_batch(client: TestClient) -> None:
    person = _create_person(client)
    tag1 = _create_tag(client, "同事")
    tag2 = _create_tag(client, "跑友")
    resp = client.put(
        f"/api/persons/{person['id']}/tags",
        json={"tag_ids": [tag1["id"], tag2["id"]]},
    )
    assert resp.status_code == 200
    assert {t["name"] for t in resp.json()["data"]["tags"]} == {"同事", "跑友"}

    resp = client.put(f"/api/persons/{person['id']}/tags", json={"tag_ids": [tag1["id"]]})
    assert {t["name"] for t in resp.json()["data"]["tags"]} == {"同事"}

    resp = client.get(f"/api/persons?tag_id={tag2['id']}")
    assert resp.json()["data"]["total"] == 0


def test_facts_crud_and_validation(client: TestClient) -> None:
    person = _create_person(client)
    resp = client.post(
        f"/api/persons/{person['id']}/facts",
        json={
            "fact_type": "喜好",
            "content": "喜欢喝美式咖啡",
            "source_type": "person",
            "confidence": "confirmed",
            "is_sensitive": False,
        },
    )
    assert resp.status_code == 200
    fact = resp.json()["data"]
    assert fact["fact_type"] == "喜好"

    resp = client.patch(
        f"/api/person-facts/{fact['id']}",
        json={"confidence": "outdated"},
    )
    assert resp.json()["data"]["confidence"] == "outdated"

    resp = client.post(
        f"/api/persons/{person['id']}/facts",
        json={"fact_type": "x", "content": "y", "confidence": "不存在的值"},
    )
    assert resp.status_code == 422

    assert client.delete(f"/api/person-facts/{fact['id']}").status_code == 204


def test_dates_crud(client: TestClient) -> None:
    person = _create_person(client)
    resp = client.post(
        f"/api/persons/{person['id']}/dates",
        json={"title": "生日", "kind": "birthday", "date_value": "1995-05-20"},
    )
    assert resp.status_code == 200
    item = resp.json()["data"]
    assert item["date_value"] == "1995-05-20"

    resp = client.get(f"/api/persons/{person['id']}/dates")
    assert resp.json()["data"]["total"] == 1
    assert client.delete(f"/api/important-dates/{item['id']}").status_code == 204


def test_follow_ups_crud(client: TestClient) -> None:
    person = _create_person(client)
    resp = client.post(
        f"/api/persons/{person['id']}/follow-ups",
        json={"title": "下周问问他新工作进展"},
    )
    assert resp.status_code == 200
    task = resp.json()["data"]
    assert task["completed"] is False

    resp = client.patch(
        f"/api/follow-up-tasks/{task['id']}",
        json={"completed": True},
    )
    assert resp.json()["data"]["completed"] is True
    assert client.delete(f"/api/follow-up-tasks/{task['id']}").status_code == 204


def test_audit_log_written_on_create(client: TestClient) -> None:
    _create_person(client, "审计员")
    with SessionLocal() as db:
        logs = db.query(AuditLog).filter(AuditLog.entity_type == "persons").all()
    assert len(logs) >= 1
    assert logs[0].action == "create"
    assert uuid.UUID(logs[0].entity_id)


def test_unknown_person_returns_404(client: TestClient) -> None:
    missing = uuid.uuid4()
    assert client.get(f"/api/persons/{missing}").status_code == 404
    assert client.patch(f"/api/persons/{missing}", json={"name": "x"}).status_code == 404
