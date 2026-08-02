"""Socialization 桌面入口：内置 FastAPI 服务 + pywebview 窗口。"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path


def _exe_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _bundle_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def main() -> None:
    data_dir = _exe_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DATA_DIR", str(data_dir))
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{data_dir / 'socialization.db'}")
    os.environ.setdefault("SOCIALIZATION_PORT", "8765")

    backend_dir = _bundle_dir() / "backend"
    if backend_dir.is_dir():
        sys.path.insert(0, str(backend_dir))
    sys.path.insert(0, str(_bundle_dir()))

    _run_migrations()

    port = int(os.environ["SOCIALIZATION_PORT"])
    from app.main import app as fastapi_app

    import uvicorn

    def run_server() -> None:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=port, log_level="warning")

    if os.environ.get("SOCIALIZATION_HEADLESS") == "1":
        run_server()
        return

    import webview

    threading.Thread(target=run_server, daemon=True).start()
    webview.create_window(
        "Socialization",
        f"http://127.0.0.1:{port}",
        width=1280,
        height=860,
        min_size=(960, 640),
    )
    webview.start()


def _run_migrations() -> None:
    """桌面版首次启动时自动执行数据库迁移（含种子数据）。"""
    bundle = _bundle_dir()
    ini = bundle / "alembic.ini"
    migrations = bundle / "migrations"
    if not ini.exists() or not migrations.is_dir():
        # 开发模式：迁移由 scripts/setup.ps1 负责
        return
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(ini))
    cfg.set_main_option("script_location", str(migrations))
    cfg.set_main_option(
        "sqlalchemy.url", os.environ["DATABASE_URL"].replace("%", "%%")
    )
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    main()
