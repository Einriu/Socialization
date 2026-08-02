"""SQLite 引擎 PRAGMA 与连接配置测试。"""

from __future__ import annotations

from sqlalchemy import text

from app.core.database import engine


def test_sqlite_pragmas_applied() -> None:
    with engine.connect() as conn:
        journal_mode = conn.execute(text("PRAGMA journal_mode")).scalar()
        foreign_keys = conn.execute(text("PRAGMA foreign_keys")).scalar()
        busy_timeout = conn.execute(text("PRAGMA busy_timeout")).scalar()
    assert journal_mode == "wal"
    assert foreign_keys == 1
    assert busy_timeout == 5000


def test_select_1_works() -> None:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    assert result == 1
