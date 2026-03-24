"""Bug report models."""

from __future__ import annotations

from pydantic import BaseModel


class BugReport(BaseModel):
    id: str
    execution_id: str
    test_case_id: str | None = None
    title: str
    severity: str  # critical | high | medium | low
    description: str
    steps_to_reproduce: list[str] = []
    expected_result: str = ""
    actual_result: str = ""
    environment: str = ""
    jira_key: str | None = None
    status: str = "open"  # open | reported | closed
