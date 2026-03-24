"""Pipeline routes — start runs, check status."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks

from app.models.pipeline import PipelineRunRequest, PipelineResult, PipelineStatus
from app.orchestrator.pipeline import run_pipeline
from app.orchestrator.state import PipelineState
from app.services import execution_service, story_service

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineStatus)
async def start_pipeline(
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
) -> PipelineStatus:
    """Start a new pipeline run for a story.

    Returns immediately with execution_id.
    The pipeline runs in the background, streaming events via WebSocket.
    """
    story = story_service.get_story(request.story_id)
    execution_id = f"run-{uuid4().hex[:8]}"

    state = PipelineState(
        execution_id=execution_id,
        story_id=story.id,
        framework=request.framework,
    )
    execution_service.store_state(state)

    async def _run() -> None:
        result_state = await run_pipeline(state, story)
        execution_service.save_execution(result_state, story.title)

    background_tasks.add_task(_run)

    return PipelineStatus(
        execution_id=execution_id,
        story_id=story.id,
        status="queued",
    )


@router.get("/status/{execution_id}", response_model=PipelineStatus)
async def get_pipeline_status(execution_id: str) -> PipelineStatus:
    """Get current status of a pipeline run."""
    state = execution_service.get_state(execution_id)
    if not state:
        return PipelineStatus(
            execution_id=execution_id,
            story_id="",
            status="failed",
            error="Execution not found",
        )
    return PipelineStatus(
        execution_id=state.execution_id,
        story_id=state.story_id,
        status=state.phase.value,
        current_agent=state.current_agent,
        agents_completed=state.agents_completed,
        started_at=state.started_at,
        completed_at=state.completed_at,
        error=state.error,
    )


@router.get("/result/{execution_id}", response_model=PipelineResult)
async def get_pipeline_result(execution_id: str) -> PipelineResult:
    """Get full results of a completed pipeline run."""
    state = execution_service.get_state(execution_id)
    if not state:
        raise ValueError("Execution not found")
    return PipelineResult(
        execution_id=state.execution_id,
        story_id=state.story_id,
        framework=state.framework,
        status=state.phase.value,
        agents_output=state.outputs,
        test_cases_generated=state.test_cases_generated,
        tests_passed=state.tests_passed,
        tests_failed=state.tests_failed,
        tests_skipped=state.tests_skipped,
        coverage_percent=state.coverage_percent,
        duration_ms=state.duration_ms,
        verdict=state.verdict,
    )
