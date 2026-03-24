"""Pydantic schemas — mirrors the frontend TypeScript interfaces exactly."""

# New models added for complete backend
from app.models.bugs import BugReport  # noqa: F401
from app.models.artifacts import Artifact  # noqa: F401
from app.models.scheduler import ScheduledJob, CreateScheduledJobRequest  # noqa: F401
from app.models.webhooks import WebhookEvent, WebhookTriggerResponse  # noqa: F401
