"""GitHub webhook handler — trigger pipelines on push/PR events."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

import structlog
from pydantic import BaseModel

from app.config import settings

logger = structlog.get_logger()


class WebhookPayload(BaseModel):
    """Parsed GitHub webhook payload."""

    event_type: str  # "push" | "pull_request"
    action: str  # "opened" | "synchronize" | "closed"
    repo_name: str
    branch: str
    commit_sha: str
    pr_number: int | None = None
    pr_title: str | None = None
    sender: str = ""


def verify_signature(payload_body: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256.

    The signature header is: sha256=<hex_digest>
    """
    secret = settings.github_webhook_secret
    if not secret:
        logger.warning("github_webhook_secret_not_set")
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    provided = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


def parse_push_event(payload: dict[str, Any]) -> WebhookPayload:
    """Parse a GitHub push webhook payload."""
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")

    return WebhookPayload(
        event_type="push",
        action="push",
        repo_name=payload.get("repository", {}).get("full_name", ""),
        branch=branch,
        commit_sha=payload.get("after", ""),
        sender=payload.get("sender", {}).get("login", ""),
    )


def parse_pull_request_event(payload: dict[str, Any]) -> WebhookPayload:
    """Parse a GitHub pull_request webhook payload."""
    pr = payload.get("pull_request", {})

    return WebhookPayload(
        event_type="pull_request",
        action=payload.get("action", ""),
        repo_name=payload.get("repository", {}).get("full_name", ""),
        branch=pr.get("head", {}).get("ref", ""),
        commit_sha=pr.get("head", {}).get("sha", ""),
        pr_number=pr.get("number"),
        pr_title=pr.get("title"),
        sender=payload.get("sender", {}).get("login", ""),
    )


def should_trigger_pipeline(payload: WebhookPayload) -> bool:
    """
    Decide if this webhook event should trigger a QA pipeline.

    Triggers on:
    - Push to main/develop branches
    - PR opened or updated (synchronize)
    """
    if payload.event_type == "push":
        return payload.branch in ("main", "master", "develop")

    if payload.event_type == "pull_request":
        return payload.action in ("opened", "synchronize", "reopened")

    return False
