"""备份、导入导出与 Markdown 导出测试。"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.services.backup_service import EXPORT_TABLES


def _db_path() -> str:
    return get_settings().database_url[len("sqlite:///") :]


def _clear_all_tables() -> None:
    conn = sqlite3.connect(_db_path())
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        for table in reversed(EXPORT_TABLES):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
    finally:
        conn.close()


def test_export_json_contains_data(client: TestClient) -> None:
    client.post("/api/persons", json={"name": "导出测试人"})
    resp = client.get("/api/export/json")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["persons"]) == 1
    assert data["persons"][0]["name"] == "导出测试人"


def test_import_roundtrip(client: TestClient) -> None:
    person = client.post("/api/persons", json={"name": "导入测试人"}).json()["data"]
    topic = client.post("/api/topics", json={"name": "导入测试话题"}).json()["data"]
    client.post(
        "/api/interactions",
        json={"title": "导入测试互动", "participant_ids": [person["id"]]},
    )
    exported = client.get("/api/export/json").json()["data"]

    _clear_all_tables()
    assert client.get("/api/persons").json()["data"]["total"] == 0

    resp = client.post("/api/import", json=exported)
    assert resp.status_code == 200
    counts = resp.json()["data"]["imported"]
    assert counts["persons"] == 1
    assert counts["topics"] == 1
    assert counts["interactions"] == 1
    assert client.get("/api/persons").json()["data"]["total"] == 1
    assert client.get("/api/topics").json()["data"]["total"] == 1
    assert topic["id"] == client.get(f"/api/topics/{topic['id']}").json()["data"]["id"]


def test_import_rejects_unknown_table(client: TestClient) -> None:
    resp = client.post("/api/import", json={"nope": []})
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_create_backup_and_list(client: TestClient) -> None:
    resp = client.post("/api/backups")
    assert resp.status_code == 200
    backup = resp.json()["data"]
    assert backup["filename"].startswith("socialization-")
    assert backup["size_bytes"] > 0

    backups = client.get("/api/backups").json()["data"]
    assert any(item["id"] == backup["id"] for item in backups)
    backup_path = Path(get_settings().data_dir) / "backups" / backup["filename"]
    assert backup_path.exists()


def test_restore_requires_confirm(client: TestClient) -> None:
    backup = client.post("/api/backups").json()["data"]
    resp = client.post(f"/api/backups/{backup['id']}/restore")
    assert resp.status_code == 400


def test_restore_roundtrip(client: TestClient) -> None:
    person = client.post("/api/persons", json={"name": "恢复测试人"}).json()["data"]
    backup = client.post("/api/backups").json()["data"]

    assert client.delete(f"/api/persons/{person['id']}/permanent?confirm=true").status_code == 204
    assert client.get("/api/persons").json()["data"]["total"] == 0

    resp = client.post(f"/api/backups/{backup['id']}/restore?confirm=true")
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["journal_mode"] == "wal"

    persons = client.get("/api/persons").json()["data"]
    assert persons["total"] == 1
    assert persons["items"][0]["name"] == "恢复测试人"


def test_markdown_export(client: TestClient) -> None:
    person = client.post("/api/persons", json={"name": "Markdown 人"}).json()["data"]
    client.post(
        f"/api/persons/{person['id']}/facts",
        json={"fact_type": "喜好", "content": "喜欢钓鱼"},
    )
    resp = client.get(f"/api/export/persons/{person['id']}.md")
    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"]
    assert "Markdown 人" in resp.text
    assert "喜欢钓鱼" in resp.text

    topic = client.post("/api/topics", json={"name": "Markdown 话题"}).json()["data"]
    resp = client.get(f"/api/export/topics/{topic['id']}.md")
    assert "Markdown 话题" in resp.text
