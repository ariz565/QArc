"""Test case schemas — maps to frontend TestCase interface."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


TestCaseType = Literal["functional", "edge", "security", "performance", "accessibility"]
TestCasePriority = Literal["P0", "P1", "P2", "P3"]
TestCaseStatus = Literal["pending", "pass", "fail", "running", "skipped"]


class TestCase(BaseModel):
    id: str
    name: str
    type: TestCaseType
    priority: TestCasePriority
    scenario: str
    steps: list[str]
    expected: str
    status: TestCaseStatus = "pending"
    duration: str | None = None
    automation_code: str | None = None
    story_id: str | None = None
