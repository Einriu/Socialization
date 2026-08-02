"""按 provider_type 实例化适配器。"""

from __future__ import annotations

from app.models.ai import AIProvider
from app.providers.base import BaseAIProvider, ProviderError
from app.providers.deepseek_provider import DeepSeekProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.openai_provider import OpenAIProvider

_REGISTRY: dict[str, type[BaseAIProvider]] = {
    "openai_compatible": OpenAICompatibleProvider,
    "deepseek": DeepSeekProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def build_provider(provider: AIProvider, api_key: str | None) -> BaseAIProvider:
    """根据提供商记录构建适配器实例。"""
    provider_cls = _REGISTRY.get(provider.provider_type)
    if provider_cls is None:
        raise ProviderError(f"不支持的提供商类型：{provider.provider_type}")
    kwargs: dict[str, object] = {
        "api_key": api_key,
        "timeout_seconds": provider.timeout_seconds,
        "max_retries": provider.max_retries,
        "proxy": provider.proxy,
        "custom_headers": provider.custom_headers,
    }
    if provider.base_url:
        kwargs["base_url"] = provider.base_url
    return provider_cls(**kwargs)
