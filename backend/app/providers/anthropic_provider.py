"""Anthropic Claude provider."""

from __future__ import annotations

import time
from typing import AsyncIterator

import anthropic

from app.providers.base import LLMMessage, LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    provider_name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Anthropic separates system prompt from messages
        system_prompt = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        resp = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt.strip() or anthropic.NOT_GIVEN,
            messages=chat_messages,
            temperature=temperature,
        )
        content = resp.content[0].text if resp.content else ""
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider_name,
            prompt_tokens=resp.usage.input_tokens,
            completion_tokens=resp.usage.output_tokens,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        system_prompt = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        async with self._client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt.strip() or anthropic.NOT_GIVEN,
            messages=chat_messages,
            temperature=temperature,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def health_check(self) -> tuple[bool, float]:
        start = time.perf_counter()
        try:
            # Quick model list check
            await self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            elapsed = (time.perf_counter() - start) * 1000
            return True, elapsed
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            return False, elapsed
