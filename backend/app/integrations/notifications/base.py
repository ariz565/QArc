"""Abstract notification interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NotificationPayload:
    """Standard notification payload across all channels."""

    execution_id: str
    story_id: str
    story_title: str
    status: str  # "completed" | "failed"
    passed: int
    failed: int
    coverage: float
    verdict: str | None = None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.failed == 0 and self.status == "completed"

    @property
    def summary(self) -> str:
        icon = "✅" if self.is_success else "❌"
        return (
            f"{icon} {self.story_id} — {self.story_title}\n"
            f"Passed: {self.passed} | Failed: {self.failed} | Coverage: {self.coverage}%"
        )


class BaseNotifier(ABC):
    """Abstract notification channel."""

    channel_name: str = ""

    @abstractmethod
    async def send(self, payload: NotificationPayload) -> bool:
        """Send notification. Returns True if successful."""
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if this channel has required configuration."""
        ...
