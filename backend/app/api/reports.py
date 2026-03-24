"""Reports routes — coverage and quality reports."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.reports import CoverageBreakdown, QualityReport
from app.services import execution_service, story_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/coverage/{execution_id}", response_model=QualityReport)
async def get_coverage_report(execution_id: str) -> QualityReport:
    """Get coverage report for a specific execution."""
    state = execution_service.get_state(execution_id)
    if not state:
        from app.core import QANexusError
        raise QANexusError(f"Execution '{execution_id}' not found", 404)

    story = story_service.get_story(state.story_id)

    return QualityReport(
        story_id=state.story_id,
        story_title=story.title,
        total_tests=state.tests_passed + state.tests_failed + state.tests_skipped,
        passed=state.tests_passed,
        failed=state.tests_failed,
        skipped=state.tests_skipped,
        coverage=CoverageBreakdown(
            functional=min(state.coverage_percent + 5, 100),
            edge=max(state.coverage_percent - 10, 0),
            security=max(state.coverage_percent - 5, 0),
            performance=max(state.coverage_percent - 20, 0),
            accessibility=max(state.coverage_percent - 15, 0),
        ),
        overall_coverage=state.coverage_percent,
        verdict=state.verdict or "PENDING",
        recommendations=[
            "Increase edge case coverage for error scenarios",
            "Add performance benchmarks for critical paths",
            "Consider accessibility testing for public-facing flows",
        ],
    )


@router.get("/summary", response_model=list[QualityReport])
async def get_all_reports() -> list[QualityReport]:
    """Get summary reports for all completed executions."""
    runs, _ = execution_service.list_executions(limit=20)
    reports = []
    for run in runs:
        if run.status == "completed":
            state = execution_service.get_state(run.id)
            if state:
                report = QualityReport(
                    story_id=run.story_id,
                    story_title=run.story_title,
                    total_tests=run.total_tests,
                    passed=run.passed,
                    failed=run.failed,
                    skipped=run.skipped,
                    coverage=CoverageBreakdown(
                        functional=min(run.coverage + 5, 100),
                        edge=max(run.coverage - 10, 0),
                        security=max(run.coverage - 5, 0),
                        performance=max(run.coverage - 20, 0),
                        accessibility=max(run.coverage - 15, 0),
                    ),
                    overall_coverage=run.coverage,
                    verdict=run.verdict or "PENDING",
                    recommendations=[],
                )
                reports.append(report)
    return reports
