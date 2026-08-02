"""DeepSeek 提供商（OpenAI 兼容预设）。"""

from __future__ import annotations

from app.providers.openai_compatible import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    """DeepSeek 预设：默认 Base URL，模型名不写死。"""

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("base_url", "https://api.deepseek.com")
        super().__init__(**kwargs)
