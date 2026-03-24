"""Slack notification — send test results via webhook.

Uses a reusable httpx.AsyncClient for connection pooling.
"""

from __future__ import annotations

import httpx
import structlog

from app.config import settings
from app.integrations.notifications.base import BaseNotifier, NotificationPayload

logger = structlog.get_logger()

_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


class SlackNotifier(BaseNotifier):
    """Send pipeline results to Slack via incoming webhook."""

    channel_name = "slack"

    def __init__(self, webhook_url: str | None = None):
        self._webhook_url = webhook_url or settings.slack_webhook_url
        self._client: httpx.AsyncClient | None = None

    def is_configured(self) -> bool:
        return bool(self._webhook_url)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=_TIMEOUT)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def send(self, payload: NotificationPayload) -> bool:
        if not self.is_configured():
            return False

        color = "#36a64f" if payload.is_success else "#dc3545"
        status_text = "Pipeline Passed ✅" if payload.is_success else "Pipeline Failed ❌"

        slack_payload = {
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"QA Nexus — {status_text}",
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": f"*Story:*\n{payload.story_id} — {payload.story_title}"},
                                {"type": "mrkdwn", "text": f"*Execution:*\n`{payload.execution_id}`"},
                                {"type": "mrkdwn", "text": f"*Passed:*\n{payload.passed}"},
                                {"type": "mrkdwn", "text": f"*Failed:*\n{payload.failed}"},
                                {"type": "mrkdwn", "text": f"*Coverage:*\n{payload.coverage}%"},
                                {"type": "mrkdwn", "text": f"*Verdict:*\n{payload.verdict or 'PENDING'}"},
                            ],
                        },
                    ],
                }
            ]
        }

        if payload.error:
            # Truncate and escape for Slack mrkdwn safety
            safe_error = payload.error[:500].replace("`", "'")
            slack_payload["attachments"][0]["blocks"].append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Error:* ```{safe_error}```"},
            })

        try:
            client = await self._get_client()
            resp = await client.post(self._webhook_url, json=slack_payload)
            resp.raise_for_status()
            logger.info("slack_sent", execution_id=payload.execution_id)
            return True
        except Exception as e:
            logger.error("slack_failed", execution_id=payload.execution_id, error=str(e))
            return False
