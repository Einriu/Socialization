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

from app.core.database import SessionLocal  # noqa: E402
from app.core.database import engine as app_engine  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import Base as ModelBase  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _prepare_db() -> None:
    """会话开始前建表，结束后释放引擎并清理临时数据库文件。"""
    ModelBase.metadata.create_all(bind=app_engine)
    yield
    app_engine.dispose()
    for suffix in ("", "-wal", "-shm"):
        candidate = Path(f"{_TEST_DB_PATH}{suffix}")
        if candidate.exists():
            try:
                candidate.unlink()
            except OSError:
                pass


@pytest.fixture(autouse=True)
def _clean_between_tests() -> None:
    """每个测试前清空全部表，避免用例之间数据串扰。"""
    with SessionLocal() as db:
        for table in reversed(ModelBase.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    yield


@pytest.fixture()
def client() -> TestClient:
    """为每个测试提供独立的 FastAPI 测试客户端。"""
    with TestClient(create_app()) as test_client:
        yield test_client
