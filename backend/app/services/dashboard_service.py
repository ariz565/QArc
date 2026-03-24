"""Dashboard service — aggregated stats and trends."""

from __future__ import annotations

from app.models.dashboard import DashboardStats, WeeklyDataPoint, WeeklyTrend
from app.services.execution_service import _executions, _pipeline_states


def get_stats() -> DashboardStats:
    """Compute dashboard stats from execution history."""
    runs = list(_executions.values())
    if not runs:
        # Return demo defaults when no real runs exist
        return DashboardStats(
            total_tests=1247,
            passed=1183,
            failed=42,
            coverage=87.3,
            avg_duration_ms=14200,
            active_pipelines=len([s for s in _pipeline_states.values() if s.phase.value == "running"]),
        )

    total = sum(r.total_tests for r in runs)
    passed = sum(r.passed for r in runs)
    failed = sum(r.failed for r in runs)
    coverage = sum(r.coverage for r in runs) / len(runs) if runs else 0
    avg_dur = sum(r.duration_ms for r in runs) // len(runs) if runs else 0
    active = len([s for s in _pipeline_states.values() if s.phase.value == "running"])

    return DashboardStats(
        total_tests=total,
        passed=passed,
        failed=failed,
        coverage=round(coverage, 1),
        avg_duration_ms=avg_dur,
        active_pipelines=active,
    )


def get_weekly_trend() -> WeeklyTrend:
    """Return weekly test trend data."""
    # Demo data — in production, aggregate from execution history
    return WeeklyTrend(data=[
        WeeklyDataPoint(day="Mon", passed=178, failed=8),
        WeeklyDataPoint(day="Tue", passed=192, failed=5),
        WeeklyDataPoint(day="Wed", passed=165, failed=12),
        WeeklyDataPoint(day="Thu", passed=201, failed=3),
        WeeklyDataPoint(day="Fri", passed=189, failed=7),
        WeeklyDataPoint(day="Sat", passed=134, failed=2),
        WeeklyDataPoint(day="Sun", passed=124, failed=5),
    ])
