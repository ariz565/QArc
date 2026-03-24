"""Notification dispatcher — sends to all configured channels in parallel."""

from __future__ import annotations

import asyncio

import structlog

from app.integrations.notifications.base import BaseNotifier, NotificationPayload
from app.integrations.notifications.slack import SlackNotifier
from app.integrations.notifications.email_notifier import EmailNotifier

logger = structlog.get_logger()


class NotificationDispatcher:
    """Fan-out notifications to all configured channels concurrently."""

    def __init__(self):
        self._channels: list[BaseNotifier] = [
            SlackNotifier(),
            EmailNotifier(),
        ]

    async def notify(self, payload: NotificationPayload) -> dict[str, bool]:
        """
        Send notification to all configured channels in parallel.
        Returns {channel_name: success_bool}.
        """
        active = [c for c in self._channels if c.is_configured()]
        if not active:
            return {}

        async def _send(channel: BaseNotifier) -> tuple[str, bool]:
            try:
                success = await channel.send(payload)
                logger.info(
                    "notification_sent",
                    channel=channel.channel_name,
                    success=success,
                    execution_id=payload.execution_id,
                )
                return channel.channel_name, success
            except Exception as e:
                logger.error(
                    "notification_error",
                    channel=channel.channel_name,
                    error=str(e),
                )
                return channel.channel_name, False

        results_list = await asyncio.gather(*[_send(c) for c in active])
        return dict(results_list)

    async def notify_on_failure_only(self, payload: NotificationPayload) -> dict[str, bool]:
        """Only send notifications if the pipeline failed."""
        if payload.is_success:
            return {}
        return await self.notify(payload)

    def available_channels(self) -> list[str]:
        """List channels that are properly configured."""
        return [c.channel_name for c in self._channels if c.is_configured()]
