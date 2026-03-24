"""Scheduled job implementations — the actual work triggered by the scheduler."""

from __future__ import annotations

from uuid import uuid4

import structlog

logger = structlog.get_logger()


async def execute_scheduled_pipeline(job_id: str, story_id: str, framework: str) -> None:
    """
    Execute a pipeline run triggered by a scheduled cron job.

    This is the function called by APScheduler when a cron trigger fires.
    """
    from app.db import async_session
    from app.db.repositories.execution_repo import ExecutionRepository
    from app.db.repositories.schedule_repo import ScheduleRepository
    from app.orchestrator.pipeline import run_pipeline
    from app.orchestrator.state import PipelineState
    from app.services.story_service import get_story
    from app.integrations.notifications.base import NotificationPayload
    from app.integrations.notifications.dispatcher import NotificationDispatcher

    execution_id = f"sched-{uuid4().hex[:8]}"
    logger.info(
        "scheduled_pipeline_start",
        job_id=job_id,
        story_id=story_id,
        execution_id=execution_id,
    )

    try:
        # Get story
        story = get_story(story_id)

        # Create pipeline state
        state = PipelineState(
            execution_id=execution_id,
            story_id=story_id,
            framework=framework,
        )

        # Run pipeline
        result_state = await run_pipeline(state, story)

        # Persist to DB
        async with async_session() as session:
            exec_repo = ExecutionRepository(session)
            await exec_repo.save_from_state(result_state, story.title)

            # Update last run timestamp
            sched_repo = ScheduleRepository(session)
            await sched_repo.update_last_run(job_id)

        # Send notifications
        dispatcher = NotificationDispatcher()
        await dispatcher.notify(NotificationPayload(
            execution_id=execution_id,
            story_id=story_id,
            story_title=story.title,
            status=result_state.phase.value,
            passed=result_state.tests_passed,
            failed=result_state.tests_failed,
            coverage=result_state.coverage_percent,
            verdict=result_state.verdict,
            error=result_state.error,
        ))

        logger.info(
            "scheduled_pipeline_done",
            job_id=job_id,
            execution_id=execution_id,
            status=result_state.phase.value,
        )

    except Exception as e:
        logger.error(
            "scheduled_pipeline_failed",
            job_id=job_id,
            execution_id=execution_id,
            error=str(e),
        )
