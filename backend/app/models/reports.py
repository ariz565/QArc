"""Reports and coverage schemas."""

from __future__ import annotations

from pydantic import BaseModel


class CoverageBreakdown(BaseModel):
    functional: float
    edge: float
    security: float
    performance: float
    accessibility: float


class QualityReport(BaseModel):
    story_id: str
    story_title: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    coverage: CoverageBreakdown
    overall_coverage: float
    verdict: str
    recommendations: list[str]
