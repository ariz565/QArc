"""Dashboard schemas — stats, trends, and metrics."""

from __future__ import annotations

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_tests: int
    passed: int
    failed: int
    coverage: float
    avg_duration_ms: int
    active_pipelines: int


class WeeklyDataPoint(BaseModel):
    day: str
    passed: int
    failed: int


class WeeklyTrend(BaseModel):
    data: list[WeeklyDataPoint]
