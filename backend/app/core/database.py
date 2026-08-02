"""SQLite 数据库引擎与会话管理。"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def _set_sqlite_pragma(dbapi_connection: Any, _connection_record: Any) -> None:
    """每次新建 SQLite 连接时应用 WAL、外键与忙等待 PRAGMA。"""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
    finally:
        cursor.close()


def create_db_engine(database_url: str = settings.database_url) -> Engine:
    """创建数据库引擎；SQLite 额外配置线程安全与 PRAGMA 事件。"""
    connect_args: dict[str, Any] = {}
    if database_url.startswith("sqlite:///"):
        connect_args["check_same_thread"] = False
    engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
    if database_url.startswith("sqlite:///"):
        event.listen(engine, "connect", _set_sqlite_pragma)
    return engine


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session]:
    """FastAPI 依赖：提供请求级数据库会话。"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database() -> dict[str, Any]:
    """执行 SELECT 1 并读取 journal_mode，返回数据库健康信息。"""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        journal_mode = conn.execute(text("PRAGMA journal_mode")).scalar()
    return {
        "connected": True,
        "select_1_ok": True,
        "journal_mode": str(journal_mode),
    }
