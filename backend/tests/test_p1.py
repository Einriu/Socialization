"""P1 知识库测试：文件上传/解析/检索、自定义字段、搜索、CSV 导入、对话压缩。"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _upload_txt(client: TestClient, content: str, filename: str = "note.txt") -> dict:
    resp = client.post(
        "/api/documents/upload",
        files={"file": (filename, content.encode("utf-8"), "text/plain")},
    )
    assert resp.status_code == 200
    document = resp.json()["data"]
    processed = client.post(f"/api/documents/{document['id']}/process").json()["data"]
    assert processed["status"] == "completed"
    return processed


def test_upload_process_and_chunks(client: TestClient) -> None:
    document = _upload_txt(
        client,
        "咖啡豆的产地决定了风味。埃塞俄比亚的咖啡带有花果香。\n" * 20,
        "coffee.txt",
    )
    assert document["status"] == "completed"
    assert document["chunk_count"] >= 1
    assert document["filename"] == "coffee.txt"

    chunks = client.get(f"/api/documents/{document['id']}/chunks").json()["data"]
    assert chunks["total"] == document["chunk_count"]
    assert "咖啡豆" in chunks["items"][0]["content"]


def test_upload_dedupe(client: TestClient) -> None:
    content = "去重测试内容" * 30
    first = _upload_txt(client, content, "a.txt")
    second = _upload_txt(client, content, "b.txt")
    assert first["id"] == second["id"]


def test_html_parse(client: TestClient) -> None:
    document = _upload_txt(
        client,
        "<html><body><h1>标题</h1><p>正文内容段落</p></body></html>",
        "page.html",
    )
    assert document["status"] == "completed"
    chunks = client.get(f"/api/documents/{document['id']}/chunks").json()["data"]
    assert "正文内容段落" in chunks["items"][0]["content"]


def test_document_links_and_filter(client: TestClient) -> None:
    person = client.post("/api/persons", json={"name": "文件关联人"}).json()["data"]
    document = _upload_txt(client, "关于运动营养的记录内容。" * 10)
    resp = client.put(
        f"/api/documents/{document['id']}/links",
        json={"person_id": person["id"]},
    )
    assert resp.status_code == 200
    assert person["id"] in resp.json()["data"]["person_ids"]
    filtered = client.get(f"/api/documents?person_id={person['id']}").json()["data"]
    assert filtered["total"] == 1


def test_search_finds_persons_topics_and_documents(client: TestClient) -> None:
    client.post("/api/persons", json={"name": "搜索引擎人"})
    client.post("/api/topics", json={"name": "搜索话题"})
    _upload_txt(client, "这是用于搜索验证的独特关键词：量子玫瑰。")
    result = client.get("/api/search?q=量子玫瑰").json()["data"]
    assert len(result["documents"]) >= 1
    result = client.get("/api/search?q=搜索引擎人").json()["data"]
    assert any(item["name"] == "搜索引擎人" for item in result["persons"])
    result = client.get("/api/search?q=搜索话题").json()["data"]
    assert any(item["name"] == "搜索话题" for item in result["topics"])


def test_custom_fields_crud_and_values(client: TestClient) -> None:
    field = client.post(
        "/api/custom-fields",
        json={"field_type": "text", "name": "喜欢的咖啡", "group_name": "喜好"},
    ).json()["data"]
    person = client.post("/api/persons", json={"name": "字段人"}).json()["data"]
    resp = client.put(
        f"/api/persons/{person['id']}/custom-values",
        json={"values": {field["id"]: "美式"}},
    )
    assert resp.status_code == 200
    assert resp.json()["data"][field["id"]] == "美式"
    values = client.get(f"/api/persons/{person['id']}/custom-values").json()["data"]
    assert values[field["id"]] == "美式"
    fields = client.get("/api/custom-fields").json()["data"]
    assert any(item["name"] == "喜欢的咖啡" for item in fields)


def test_csv_persons_import(client: TestClient) -> None:
    csv_content = "name,nickname,organization\n张三,三哥,某公司\n李四,,另一家\n"
    resp = client.post(
        "/api/import/persons-csv",
        files={"file": ("persons.csv", csv_content.encode("utf-8-sig"), "text/csv")},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["created"] == 2
    persons = client.get("/api/persons").json()["data"]
    assert persons["total"] == 2


def test_conversation_summarize(
    client: TestClient, monkeypatch: object
) -> None:
    class FakeChatProvider:
        async def chat(self, request: object) -> object:
            from app.providers.base import ChatResponse

            return ChatResponse(content="这是摘要")

    provider_row = client.post(
        "/api/providers",
        json={"name": "摘要提供商", "provider_type": "openai_compatible", "api_key": "sk-x"},
    ).json()["data"]
    model = client.post(
        f"/api/providers/{provider_row['id']}/models",
        json={"model_id": "sum-model"},
    ).json()["data"]
    conversation = client.post("/api/conversations", json={}).json()["data"]
    client.patch(
        f"/api/conversations/{conversation['id']}",
        json={"provider_id": provider_row["id"], "model_id": model["id"]},
    )
    monkeypatch.setattr(
        "app.services.conversation_service.build_provider",
        lambda provider, api_key: FakeChatProvider(),
    )
    resp = client.post(f"/api/conversations/{conversation['id']}/summarize")
    assert resp.status_code == 200
    assert resp.json()["data"]["summary"] == "这是摘要"
    updated = client.get(f"/api/conversations/{conversation['id']}").json()["data"]
    assert updated["summary"] == "这是摘要"
