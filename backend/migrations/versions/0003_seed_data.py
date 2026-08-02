"""写入种子数据：预设话题分类、默认设置、内置 Prompt 模板。

Revision ID: 0003_seed_data
Revises: 0002_p0_tables
Create Date: 2026-08-02
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision = "0003_seed_data"
down_revision = "0002_p0_tables"
branch_labels = None
depends_on = None


def _now() -> datetime:
    return datetime.now(UTC)


def _uid() -> str:
    return uuid.uuid4().hex


TOPIC_CATEGORIES = [
    "日常生活",
    "工作与职业",
    "学习与教育",
    "科技与数码",
    "电影与电视剧",
    "音乐",
    "游戏",
    "运动",
    "健身与健康常识",
    "美食",
    "咖啡与茶",
    "旅行",
    "城市与地域文化",
    "汽车",
    "时尚与消费",
    "宠物",
    "情感与关系",
    "社会新闻",
    "历史与文化",
    "个人成长",
]

PROMPT_TEMPLATES = [
    (
        "general",
        "通用社交助手",
        "你是一位友好的社交助手。请用自然、真诚、简洁的中文回答，避免说教。",
    ),
    (
        "person_profile",
        "人物档案整理",
        "根据用户提供的信息，整理人物档案。区分事实与推测，推测必须标注为未确认。",
    ),
    (
        "interaction_extract",
        "互动信息提取",
        "从互动记录中提取人物新信息、喜好、待办事项与可继续追问的内容，输出为待确认列表。",
    ),
    (
        "chat_prep",
        "聊天准备",
        "根据人物档案与最近互动，生成聊天简报：延续话题、避免重复询问的内容、开场方式与边界提醒。",
    ),
    (
        "chat_review",
        "聊天复盘",
        "根据互动记录进行复盘，从倾听、追问、表达、共情等角度给出具体反馈，不把推测写成事实。",
    ),
    (
        "topic_tutor",
        "话题导师",
        "以容易理解的方式讲解话题知识，并生成由浅入深的讨论问题与自然聊天表达。",
    ),
    (
        "document_qa",
        "文件问答",
        "只基于用户提供的资料回答问题，并说明引用来源；资料不足时明确说明。",
    ),
    (
        "practice",
        "模拟聊天",
        "扮演用户指定的角色进行模拟对话，对话结束后从倾听、追问、表达、共情、节奏与边界感等维度评分并给出证据。",
    ),
    (
        "reply_suggestion",
        "消息回复建议",
        "根据上下文给出自然、真诚、得体的消息回复建议，并说明理由。",
    ),
    (
        "weekly_report",
        "周报生成",
        "根据本周互动数据生成成长周报：概况、表现、重复问题与下周建议。",
    ),
]


def upgrade() -> None:
    now = _now()

    categories = sa.table(
        "topic_categories",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("parent_id", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    op.bulk_insert(
        categories,
        [
            {"id": _uid(), "name": name, "parent_id": None, "created_at": now, "updated_at": now}
            for name in TOPIC_CATEGORIES
        ],
    )

    settings = sa.table(
        "app_settings",
        sa.column("id", sa.String),
        sa.column("key", sa.String),
        sa.column("value", sa.JSON),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    op.bulk_insert(
        settings,
        [
            {
                "id": _uid(),
                "key": "theme",
                "value": "system",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": _uid(),
                "key": "timezone",
                "value": "Asia/Shanghai",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": _uid(),
                "key": "locale",
                "value": "zh-CN",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

    templates = sa.table(
        "prompt_templates",
        sa.column("id", sa.String),
        sa.column("template_type", sa.String),
        sa.column("title", sa.String),
        sa.column("content", sa.Text),
        sa.column("is_editable", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    op.bulk_insert(
        templates,
        [
            {
                "id": _uid(),
                "template_type": template_type,
                "title": title,
                "content": content,
                "is_editable": True,
                "created_at": now,
                "updated_at": now,
            }
            for template_type, title, content in PROMPT_TEMPLATES
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM prompt_templates")
    op.execute("DELETE FROM app_settings")
    op.execute("DELETE FROM topic_categories")
