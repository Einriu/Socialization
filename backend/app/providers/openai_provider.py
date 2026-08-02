"""OpenAI 提供商（OpenAI 兼容预设）。"""

from __future__ import annotations

from app.providers.openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI 预设：默认 Base URL，模型名不写死。"""

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("base_url", "https://api.openai.com/v1")
        super().__init__(**kwargs)
