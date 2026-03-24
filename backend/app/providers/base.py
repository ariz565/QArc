"""Abstract LLM provider protocol — all providers implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class LLMMessage:
    role: str   # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMProvider(ABC):
    """Base contract for all LLM providers.

    Every provider must implement:
    - generate()       → full response
    - stream()         → async iterator of text chunks
    - health_check()   → connectivity test
    """

    provider_name: str = "base"

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Generate a complete response."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream response tokens one at a time."""
        ...

    @abstractmethod
    async def health_check(self) -> tuple[bool, float]:
        """Check if the provider is reachable.

        Returns (is_healthy, latency_ms).
        """
        ...
