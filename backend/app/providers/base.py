"""AI 提供商统一接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from pydantic import BaseModel, Field


class ProviderError(Exception):
    """提供商调用失败（不含密钥等敏感信息）。"""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float | None = Field(default=None, ge=0, le=2)
    max_tokens: int | None = Field(default=None, ge=1)


class ChatResponse(BaseModel):
    content: str
    usage: dict | None = None


class BaseAIProvider(ABC):
    """所有提供商必须实现的接口；业务代码不直接调用各家 SDK。"""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 60,
        max_retries: int = 2,
        proxy: str | None = None,
        custom_headers: dict | None = None,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.proxy = proxy
        self.custom_headers = custom_headers or {}

    @abstractmethod
    async def test_connection(self) -> dict:
        """测试连通性，返回 {ok, models, latency_ms}。"""

    @abstractmethod
    async def list_models(self) -> list[dict]:
        """获取模型列表：[{model_id, display_name}]。"""

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """非流式对话。"""

    @abstractmethod
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """流式对话，逐块产出增量文本。"""

    async def create_embeddings(self, model: str, texts: list[str]) -> list[list[float]]:
        """可选：生成文本向量，默认不支持。"""
        raise ProviderError("该提供商不支持嵌入")

    async def ocr_image(self, image_base64: str, model: str) -> str:
        """可选：图片文字识别（vision 模型）。默认不支持。"""
        raise ProviderError("该提供商不支持图片识别")

    async def transcribe_audio(self, file_path: str, model: str) -> str:
        """可选：音频转文字（/audio/transcriptions）。默认不支持。"""
        raise ProviderError("该提供商不支持音频转写")
