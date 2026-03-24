"""Google AI Studio (Gemini) provider."""

from __future__ import annotations

import time
from typing import AsyncIterator

from google import genai
from google.genai import types

from app.providers.base import LLMMessage, LLMProvider, LLMResponse


class GoogleAIProvider(LLMProvider):
    provider_name = "google"

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._client = genai.Client(api_key=api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        system_prompt, contents = self._split_messages(messages)
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt or None,
        )
        resp = await self._client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        text = resp.text or ""
        prompt_tok = resp.usage_metadata.prompt_token_count if resp.usage_metadata else 0
        completion_tok = resp.usage_metadata.candidates_token_count if resp.usage_metadata else 0
        return LLMResponse(
            content=text,
            model=self.model,
            provider=self.provider_name,
            prompt_tokens=prompt_tok,
            completion_tokens=completion_tok,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        system_prompt, contents = self._split_messages(messages)
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt or None,
        )
        async for chunk in self._client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                yield chunk.text

    async def health_check(self) -> tuple[bool, float]:
        start = time.perf_counter()
        try:
            await self._client.aio.models.generate_content(
                model=self.model,
                contents="ping",
                config=types.GenerateContentConfig(max_output_tokens=5),
            )
            elapsed = (time.perf_counter() - start) * 1000
            return True, elapsed
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            return False, elapsed

    @staticmethod
    def _split_messages(messages: list[LLMMessage]) -> tuple[str, list[types.Content]]:
        """Separate system prompt from chat contents."""
        system_parts: list[str] = []
        contents: list[types.Content] = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                role = "model" if m.role == "assistant" else "user"
                contents.append(types.Content(role=role, parts=[types.Part(text=m.content)]))
        return "\n".join(system_parts), contents
