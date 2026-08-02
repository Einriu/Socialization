"""通用 OpenAI 兼容接口适配器（DeepSeek/OpenAI 均基于此协议）。"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from pathlib import Path

import httpx

from app.providers.base import BaseAIProvider, ChatRequest, ChatResponse, ProviderError


class OpenAICompatibleProvider(BaseAIProvider):
    """通过 OpenAI 兼容 HTTP 协议调用任意提供商。"""

    async def _client(self) -> httpx.AsyncClient:
        headers = {"Content-Type": "application/json", **self.custom_headers}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout_seconds,
            proxy=self.proxy,
        )

    async def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        last_error: Exception | None = None
        async with await self._client() as client:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.request(method, path, json=payload)
                    if response.status_code >= 400:
                        raise ProviderError(f"提供商返回 HTTP {response.status_code}")
                    return response.json()
                except ProviderError:
                    raise
                except Exception as exc:  # noqa: BLE001 - 重试网络类错误
                    last_error = exc
                    if attempt < self.max_retries:
                        await asyncio_sleep(1 + attempt)
        raise ProviderError(f"请求失败：{type(last_error).__name__}")

    async def test_connection(self) -> dict:
        start = time.monotonic()
        data = await self._request_json("GET", "/models")
        models = data.get("data", [])
        return {
            "ok": True,
            "models": len(models),
            "latency_ms": int((time.monotonic() - start) * 1000),
        }

    async def list_models(self) -> list[dict]:
        data = await self._request_json("GET", "/models")
        return [
            {"model_id": item.get("id", ""), "display_name": item.get("id", "")}
            for item in data.get("data", [])
            if item.get("id")
        ]

    async def chat(self, request: ChatRequest) -> ChatResponse:
        payload = {"model": request.model, "messages": [m.model_dump() for m in request.messages]}
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        data = await self._request_json("POST", "/chat/completions", payload)
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return ChatResponse(content=content, usage=data.get("usage"))

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        payload = {
            "model": request.model,
            "messages": [m.model_dump() for m in request.messages],
            "stream": True,
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        async with await self._client() as client:
            async with client.stream("POST", "/chat/completions", json=payload) as response:
                if response.status_code >= 400:
                    raise ProviderError(f"提供商返回 HTTP {response.status_code}")
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        chunk = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                    if delta:
                        yield delta

    async def create_embeddings(self, model: str, texts: list[str]) -> list[list[float]]:
        """调用 /embeddings 生成向量（OpenAI 兼容）。"""
        data = await self._request_json(
            "POST", "/embeddings", {"model": model, "input": texts}
        )
        return [item["embedding"] for item in data.get("data", [])]

    async def ocr_image(self, image_base64: str, model: str) -> str:
        """调用 vision 模型识别图片中的文字。"""
        data = await self._request_json(
            "POST",
            "/chat/completions",
            {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                            },
                            {"type": "text", "text": "请识别图片中的全部文字，只输出识别结果。"},
                        ],
                    }
                ],
            },
        )
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def transcribe_audio(self, file_path: str, model: str) -> str:
        """调用 /audio/transcriptions 转写音频。"""

        async with await self._client() as client:
            audio_bytes = await asyncio.to_thread(Path(file_path).read_bytes)
            response = await client.post(
                "/audio/transcriptions",
                files={
                    "file": (Path(file_path).name, audio_bytes, "application/octet-stream")
                },
                data={"model": model, "response_format": "json"},
            )
            if response.status_code >= 400:
                raise ProviderError(f"提供商返回 HTTP {response.status_code}")
        return response.json().get("text", "")


async def asyncio_sleep(seconds: float) -> None:
    """避免在模块顶层直接依赖 asyncio 语义的辅助函数。"""
    import asyncio

    await asyncio.sleep(seconds)
