"""Scheduler models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ScheduledJob(BaseModel):
    id: str
    name: str
    story_id: str
    framework: str = "playwright"
    cron_expression: str  # "0 8 * * 1-5"
    enabled: bool = True
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None


class CreateScheduledJobRequest(BaseModel):
    name: str
    story_id: str
    framework: str = "playwright"
    cron_expression: str


class ToggleJobRequest(BaseModel):
    enabled: bool
