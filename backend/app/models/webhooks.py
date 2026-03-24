"""Webhook models."""

from __future__ import annotations

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    event_type: str
    action: str
    repo_name: str
    branch: str
    commit_sha: str
    pr_number: int | None = None
    pr_title: str | None = None
    sender: str = ""


class WebhookTriggerResponse(BaseModel):
    triggered: bool
    execution_id: str | None = None
    reason: str = ""
