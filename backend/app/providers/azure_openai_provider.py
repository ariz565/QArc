"""Azure OpenAI provider — GPT models via Azure-managed endpoints."""

from __future__ import annotations

import time
from typing import AsyncIterator

from openai import AsyncAzureOpenAI

from app.providers.base import LLMMessage, LLMProvider, LLMResponse


class AzureOpenAIProvider(LLMProvider):
    provider_name = "azure_openai"

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment: str,
        api_version: str = "2024-12-01-preview",
    ) -> None:
        self.deployment = deployment
        self._client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        resp = await self._client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = resp.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=self.deployment,
            provider=self.provider_name,
            prompt_tokens=resp.usage.prompt_tokens if resp.usage else 0,
            completion_tokens=resp.usage.completion_tokens if resp.usage else 0,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    async def health_check(self) -> tuple[bool, float]:
        start = time.perf_counter()
        try:
            await self._client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            elapsed = (time.perf_counter() - start) * 1000
            return True, elapsed
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            return False, elapsed
