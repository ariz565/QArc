"""Pipeline schemas — run requests, status, and configuration."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PipelineRunRequest(BaseModel):
    story_id: str
    framework: str = "playwright"


class PipelineStatus(BaseModel):
    execution_id: str
    story_id: str
    status: Literal["queued", "running", "completed", "failed"]
    current_agent: str | None = None
    agents_completed: list[str] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


class PipelineResult(BaseModel):
    execution_id: str
    story_id: str
    framework: str
    status: Literal["completed", "failed"]
    agents_output: dict[str, str]  # agent_id → content
    test_cases_generated: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    coverage_percent: float
    duration_ms: int
    verdict: str | None = None
