"""Execution history schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExecutionRun(BaseModel):
    id: str
    story_id: str
    story_title: str
    framework: str
    trigger: Literal["manual", "ci", "scheduled"]
    status: Literal["completed", "failed", "running"]
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int = 0
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage: float = 0.0
    verdict: str | None = None


class ExecutionListResponse(BaseModel):
    executions: list[ExecutionRun]
    total: int
