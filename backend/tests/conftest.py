"""pytest 公共配置：使用临时 SQLite 数据库运行测试。"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_TEST_DB_DIR = Path(tempfile.gettempdir()) / "socialization-tests"
_TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
_TEST_DB_PATH = _TEST_DB_DIR / "test.db"

os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH.as_posix()}"
os.environ["APP_VERSION"] = "0.0.0-test"

from app.core.database import engine as app_engine  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _clean_test_db() -> None:
    """测试会话结束后清理临时数据库文件。"""
    yield
    app_engine.dispose()
    for suffix in ("", "-wal", "-shm"):
        candidate = Path(f"{_TEST_DB_PATH}{suffix}")
        if candidate.exists():
            try:
                candidate.unlink()
            except OSError:
                pass


@pytest.fixture()
def client() -> TestClient:
    """为每个测试提供独立的 FastAPI 测试客户端。"""
    with TestClient(create_app()) as test_client:
        yield test_client
