"""备份与导出：SQLite 快照、JSON 导入导出、Markdown 导出。"""

from __future__ import annotations

import csv
import io
import shutil
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi.responses import FileResponse, Response
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal, engine
from app.core.exceptions import AppError
from app.models.ai import Conversation, ConversationMessage
from app.models.interaction import Interaction, InteractionParticipant
from app.models.person import FollowUpTask, ImportantDate, Person, PersonFact
from app.models.support import BackupRecord
from app.models.topic import Topic, TopicNote, TopicPersonLink

EXPORT_TABLES = [
    "topic_categories",
    "persons",
    "tags",
    "person_tags",
    "person_facts",
    "important_dates",
    "topics",
    "topic_notes",
    "topic_person_links",
    "interactions",
    "interaction_participants",
    "interaction_topics",
    "follow_up_tasks",
    "ai_providers",
    "ai_models",
    "conversations",
    "conversation_messages",
    "conversation_links",
    "app_settings",
    "prompt_templates",
]

IMPORT_EXCLUDE_COLUMNS: dict[str, set[str]] = {
    "ai_providers": {"encrypted_api_key"},
}


def _db_path() -> Path:
    url = get_settings().database_url
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        raise AppError("INTERNAL_ERROR", "仅支持 SQLite 备份", status_code=500)
    return Path(url[len(prefix) :])


def _backups_dir() -> Path:
    path = Path(get_settings().data_dir) / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _snapshot(source: Path, dest: Path) -> int:
    src = sqlite3.connect(source)
    try:
        dst = sqlite3.connect(dest)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    return dest.stat().st_size


def export_json() -> dict[str, list[dict]]:
    """导出全部业务数据为 JSON（不含 API Key 明文）。"""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        data: dict[str, list[dict]] = {}
        for table in EXPORT_TABLES:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            data[table] = [dict(row) for row in rows]
        return data
    finally:
        conn.close()


def import_json(payload: dict) -> dict[str, int]:
    """导入 JSON 全量数据（先清空业务表再插入）。"""
    if not isinstance(payload, dict):
        raise AppError("VALIDATION_ERROR", "导入内容必须是对象", status_code=400)
    unknown = set(payload) - set(EXPORT_TABLES)
    if unknown:
        raise AppError("VALIDATION_ERROR", f"未知的数据表：{sorted(unknown)}", status_code=400)
    conn = sqlite3.connect(_db_path())
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        cursor = conn.cursor()
        for table in reversed(EXPORT_TABLES):
            cursor.execute(f"DELETE FROM {table}")
        counts: dict[str, int] = {}
        for table in EXPORT_TABLES:
            rows = payload.get(table, [])
            if not rows:
                counts[table] = 0
                continue
            excluded = IMPORT_EXCLUDE_COLUMNS.get(table, set())
            columns = [col for col in rows[0].keys() if col not in excluded]
            placeholders = ",".join("?" for _ in columns)
            sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            for row in rows:
                cursor.execute(sql, [row.get(col) for col in columns])
            counts[table] = len(rows)
        conn.commit()
    finally:
        conn.close()
    return counts


def import_persons_csv_from_bytes(db: Session, content: bytes) -> dict:
    """从 CSV 批量导入人物（列：name/姓名、nickname/昵称等）。"""
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    created = 0
    skipped = 0
    for row in reader:
        name = (row.get("name") or row.get("姓名") or "").strip()
        if not name:
            skipped += 1
            continue
        db.add(
            Person(
                name=name,
                nickname=row.get("nickname") or row.get("昵称") or None,
                organization=row.get("organization") or row.get("公司") or None,
                occupation=row.get("occupation") or row.get("职业") or None,
                location=row.get("location") or row.get("所在地") or None,
                relationship_type=row.get("relationship_type") or row.get("关系") or None,
            )
        )
        created += 1
    db.flush()
    return {"created": created, "skipped": skipped}


def create_backup() -> dict:
    """用 SQLite backup API 生成一致性快照并记录。"""
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    dest = _backups_dir() / f"socialization-{timestamp}.db"
    size = _snapshot(_db_path(), dest)
    with SessionLocal() as db:
        record = BackupRecord(
            filename=dest.name,
            path=str(dest),
            size_bytes=size,
            status="ok",
        )
        db.add(record)
        db.commit()
        return {
            "id": str(record.id),
            "filename": record.filename,
            "size_bytes": record.size_bytes,
            "created_at": record.created_at.isoformat(),
        }


def list_backups(db: Session) -> list[BackupRecord]:
    return list(
        db.execute(
            select(BackupRecord).order_by(BackupRecord.created_at.desc())
        ).scalars()
    )


def _verify_backup_path(backup_path: Path) -> Path:
    backups_root = _backups_dir().resolve()
    resolved = backup_path.resolve()
    if not resolved.is_relative_to(backups_root) or not resolved.exists():
        raise AppError("NOT_FOUND", "备份文件不存在", status_code=404)
    return resolved


def restore_backup(backup_id: uuid.UUID, confirm: bool) -> dict:
    """恢复备份：恢复前自动生成安全快照，然后替换数据库文件。"""
    if not confirm:
        raise AppError("CONFLICT", "需要确认参数 confirm=true", status_code=400)
    with SessionLocal() as db:
        record = db.get(BackupRecord, backup_id)
        if record is None:
            raise AppError("NOT_FOUND", status_code=404)
        backup_path = _verify_backup_path(Path(record.path))

    db_path = _db_path()
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    safety = _backups_dir() / f"pre-restore-{timestamp}.db"
    safety_size = _snapshot(db_path, safety)
    with SessionLocal() as db:
        db.add(
            BackupRecord(
                filename=safety.name,
                path=str(safety),
                size_bytes=safety_size,
                status="ok",
            )
        )
        db.commit()

    engine.dispose()
    shutil.copyfile(backup_path, db_path)
    for suffix in ("-wal", "-shm"):
        sidecar = Path(f"{db_path}{suffix}")
        if sidecar.exists():
            sidecar.unlink()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        journal_mode = conn.execute(text("PRAGMA journal_mode")).scalar()
    return {
        "restored_from": record.filename,
        "safety_snapshot": safety.name,
        "journal_mode": str(journal_mode),
    }
def download_backup(backup_id: uuid.UUID) -> FileResponse:
    with SessionLocal() as db:
        record = db.get(BackupRecord, backup_id)
        if record is None:
            raise AppError("NOT_FOUND", status_code=404)
        path = _verify_backup_path(Path(record.path))
    return FileResponse(path, filename=record.filename, media_type="application/octet-stream")


def export_person_markdown(db: Session, person_id: uuid.UUID) -> str:
    person = db.get(Person, person_id)
    if person is None or person.deleted_at is not None:
        raise AppError("NOT_FOUND", status_code=404)
    lines = [
        f"# {person.name}",
        "",
        f"- 昵称：{person.nickname or '—'}",
        f"- 关系：{person.relationship_type or '—'}",
        f"- 熟悉程度：{person.familiarity_level}/6",
        f"- 公司：{person.organization or '—'}",
        f"- 职业：{person.occupation or '—'}",
        f"- 所在地：{person.location or '—'}",
        "",
        "## 摘要",
        person.summary or "—",
        "",
        "## 事实",
    ]
    facts = db.execute(
        select(PersonFact).where(PersonFact.person_id == person_id)
    ).scalars()
    for fact in facts:
        confirmed = fact.confidence in ("confirmed", "user_observation")
        mark = "敏感" if fact.is_sensitive else "已确认" if confirmed else "未确认"
        lines.append(f"- [{mark}] {fact.fact_type}：{fact.content}")
    lines += ["", "## 重要日期"]
    dates = db.execute(
        select(ImportantDate).where(ImportantDate.person_id == person_id)
    ).scalars()
    for item in dates:
        lines.append(f"- {item.date_value} {item.title}")
    lines += ["", "## 待跟进"]
    tasks = db.execute(
        select(FollowUpTask).where(
            FollowUpTask.person_id == person_id, FollowUpTask.deleted_at.is_(None)
        )
    ).scalars()
    for task in tasks:
        state = "已完成" if task.completed else "待办"
        lines.append(f"- [{state}] {task.title}")
    lines += ["", "## 互动"]
    interactions = db.execute(
        select(Interaction)
        .join(InteractionParticipant)
        .where(
            InteractionParticipant.person_id == person_id,
            Interaction.deleted_at.is_(None),
        )
        .order_by(Interaction.occurred_at.desc())
    ).scalars()
    for item in interactions:
        lines.append(f"- {item.occurred_at.isoformat()} {item.title}（{item.summary or ''}）")
    return "\n".join(lines) + "\n"


def export_topic_markdown(db: Session, topic_id: uuid.UUID) -> str:
    topic = db.get(Topic, topic_id)
    if topic is None or topic.deleted_at is not None:
        raise AppError("NOT_FOUND", status_code=404)
    note = db.execute(
        select(TopicNote).where(TopicNote.topic_id == topic_id)
    ).scalar_one_or_none()
    persons = db.execute(
        select(Person)
        .join(TopicPersonLink)
        .where(TopicPersonLink.topic_id == topic_id)
    ).scalars()
    lines = [
        f"# 话题：{topic.name}",
        "",
        f"- 掌握程度：{topic.mastery_level}/6",
        f"- 简介：{topic.description or '—'}",
        "",
        "## 关联人物",
    ]
    lines += [f"- {person.name}" for person in persons]
    lines += ["", "## 笔记"]
    note_text = note.plain_text if note is not None else None
    lines.append(note_text or "（暂无笔记）")
    return "\n".join(lines) + "\n"


def export_conversation_markdown(db: Session, conversation_id: uuid.UUID) -> str:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.deleted_at is not None:
        raise AppError("NOT_FOUND", status_code=404)
    messages = db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.asc())
    ).scalars()
    lines = [f"# 对话：{conversation.title}", ""]
    for message in messages:
        role = "我" if message.role == "user" else "AI"
        content = message.content or ""
        if message.generated_by_ai:
            lines.append(f"**{role}（AI 生成）**：\n\n{content}")
        else:
            lines.append(f"**{role}**：\n\n{content}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def markdown_response(content: str, filename: str) -> Response:
    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
