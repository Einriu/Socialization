"""Ollama 本地模型（OpenAI 兼容预设）。"""

from __future__ import annotations

from app.providers.openai_compatible import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    """Ollama 预设：默认 Base URL，模型名由用户配置。"""

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("base_url", "http://127.0.0.1:11434/v1")
        super().__init__(**kwargs)
