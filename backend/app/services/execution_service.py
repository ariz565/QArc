"""Execution service — manages pipeline runs and history."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.executions import ExecutionRun
from app.orchestrator.state import PipelineState

# ── In-memory execution store ──
_executions: dict[str, ExecutionRun] = {}
_pipeline_states: dict[str, PipelineState] = {}


def store_state(state: PipelineState) -> None:
    """Store/update pipeline state for tracking."""
    _pipeline_states[state.execution_id] = state


def get_state(execution_id: str) -> PipelineState | None:
    return _pipeline_states.get(execution_id)


def save_execution(state: PipelineState, story_title: str) -> ExecutionRun:
    """Convert a completed pipeline state to an execution record."""
    run = ExecutionRun(
        id=state.execution_id,
        story_id=state.story_id,
        story_title=story_title,
        framework=state.framework,
        trigger="manual",
        status="completed" if state.phase.value == "completed" else "failed",
        started_at=state.started_at or datetime.now(timezone.utc),
        completed_at=state.completed_at,
        duration_ms=state.duration_ms,
        total_tests=state.tests_passed + state.tests_failed + state.tests_skipped,
        passed=state.tests_passed,
        failed=state.tests_failed,
        skipped=state.tests_skipped,
        coverage=state.coverage_percent,
        verdict=state.verdict,
    )
    _executions[run.id] = run
    return run


def list_executions(
    limit: int = 50,
    offset: int = 0,
    story_id: str | None = None,
) -> tuple[list[ExecutionRun], int]:
    """List execution history with optional filtering."""
    runs = list(_executions.values())
    if story_id:
        runs = [r for r in runs if r.story_id == story_id]
    runs.sort(key=lambda r: r.started_at, reverse=True)
    total = len(runs)
    return runs[offset : offset + limit], total


def get_execution(execution_id: str) -> ExecutionRun | None:
    return _executions.get(execution_id)
