"""LLM resilience layer — retry with exponential backoff + provider fallback.

Inspired by TradingAgents' multi-vendor fallback in dataflows/interface.py.
When the primary provider fails, we try the fallback chain before giving up.
"""

from __future__ import annotations

import asyncio
import random
from typing import AsyncIterator

import structlog

from app.providers.base import LLMMessage, LLMProvider, LLMResponse

logger = structlog.get_logger()


class RetryExhaustedError(Exception):
    """All retry attempts and fallback providers exhausted."""

    def __init__(self, agent_id: str, attempts: list[tuple[str, str]]):
        self.agent_id = agent_id
        self.attempts = attempts
        providers = ", ".join(f"{p}({e})" for p, e in attempts)
        super().__init__(f"All LLM attempts exhausted for '{agent_id}': {providers}")


class ResilientLLM:
    """Wraps an LLM provider with retry + fallback capabilities.

    Usage:
        resilient = ResilientLLM(
            primary=anthropic_provider,
            fallbacks=[openai_provider, ollama_provider],
            max_retries=3,
            base_delay=1.0,
        )
        response = await resilient.generate(messages)
    """

    def __init__(
        self,
        primary: LLMProvider,
        fallbacks: list[LLMProvider] | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        self.primary = primary
        self.fallbacks = fallbacks or []
        self.max_retries = max_retries
        self.base_delay = base_delay

    def _providers(self) -> list[LLMProvider]:
        """Build ordered provider chain: primary first, then fallbacks."""
        return [self.primary, *self.fallbacks]

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        agent_id: str = "",
    ) -> LLMResponse:
        """Generate with retry per provider + fallback chain."""
        attempts: list[tuple[str, str]] = []

        for provider in self._providers():
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = await provider.generate(
                        messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    if attempts:
                        logger.info(
                            "llm_recovered",
                            agent=agent_id,
                            provider=provider.provider_name,
                            attempt=attempt,
                            previous_failures=len(attempts),
                        )
                    return response

                except Exception as exc:
                    delay = self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    attempts.append((provider.provider_name, str(exc)[:200]))
                    logger.warning(
                        "llm_retry",
                        agent=agent_id,
                        provider=provider.provider_name,
                        attempt=attempt,
                        max_retries=self.max_retries,
                        delay=round(delay, 2),
                        error=str(exc)[:200],
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(delay)

            # All retries exhausted for this provider → try next fallback
            logger.warning(
                "llm_fallback",
                agent=agent_id,
                failed_provider=provider.provider_name,
                remaining_fallbacks=len(self._providers()) - len(attempts) // self.max_retries,
            )

        raise RetryExhaustedError(agent_id, attempts)

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        agent_id: str = "",
    ) -> AsyncIterator[str]:
        """Stream with retry per provider + fallback chain.

        NOTE: Streaming retries only catch errors before the first token.
        Once streaming starts, we commit to that provider.
        """
        attempts: list[tuple[str, str]] = []

        for provider in self._providers():
            for attempt in range(1, self.max_retries + 1):
                try:
                    async for token in provider.stream(
                        messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    ):
                        yield token
                    return  # Stream completed successfully

                except Exception as exc:
                    delay = self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    attempts.append((provider.provider_name, str(exc)[:200]))
                    logger.warning(
                        "llm_stream_retry",
                        agent=agent_id,
                        provider=provider.provider_name,
                        attempt=attempt,
                        error=str(exc)[:200],
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(delay)

        raise RetryExhaustedError(agent_id, attempts)
