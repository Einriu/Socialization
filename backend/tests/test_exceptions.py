"""统一异常响应格式测试。"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.exceptions import ERROR_MESSAGES, AppError, register_exception_handlers
from app.core.response import error_response


class _ProbeBody(BaseModel):
    name: str


def _build_probe_app() -> FastAPI:
    """仅用于测试的探针应用：验证请求体校验错误响应。"""
    probe = FastAPI()
    register_exception_handlers(probe)
    router = APIRouter()

    @router.post("/_probe")
    def probe_route(body: _ProbeBody) -> dict[str, str]:
        return {"name": body.name}

    probe.include_router(router, prefix="/api")
    return probe


def test_unknown_route_returns_unified_error(client: TestClient) -> None:
    resp = client.get("/api/does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert body == {"code": "NOT_FOUND", "message": "资源不存在", "data": None}


def test_method_not_allowed_returns_unified_error(client: TestClient) -> None:
    resp = client.post("/api/health", json={})
    assert resp.status_code == 405
    body = resp.json()
    assert body["code"] == "METHOD_NOT_ALLOWED"
    assert body["message"] == "请求方法不允许"


def test_validation_error_returns_unified_422() -> None:
    with TestClient(_build_probe_app()) as probe:
        resp = probe.post("/api/_probe", json={})
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"]
    assert "name" in body["message"]


def test_app_error_carries_code_message_status() -> None:
    err = AppError("CONFLICT", status_code=409)
    assert err.code == "CONFLICT"
    assert err.message == ERROR_MESSAGES["CONFLICT"]
    assert err.status_code == 409


def test_error_response_shape() -> None:
    payload = error_response("CONFLICT", "资源状态冲突")
    assert payload == {"code": "CONFLICT", "message": "资源状态冲突", "data": None}
