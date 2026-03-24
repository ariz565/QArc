"""Scheduler — APScheduler-based cron job runner for scheduled pipeline executions."""

from __future__ import annotations

from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import structlog

logger = structlog.get_logger()

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="UTC")
    return _scheduler


async def start_scheduler() -> None:
    """Start the APScheduler background scheduler."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("scheduler_started")


async def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("scheduler_stopped")


def add_pipeline_job(
    job_id: str,
    cron_expression: str,
    story_id: str,
    framework: str = "playwright",
) -> None:
    """
    Register a cron job that triggers a pipeline run.

    cron_expression format: "minute hour day_of_month month day_of_week"
    Examples:
      "0 8 * * 1-5"  → 8 AM weekdays
      "30 6 * * *"   → 6:30 AM daily
      "0 */4 * * *"  → Every 4 hours
    """
    scheduler = get_scheduler()

    parts = cron_expression.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expression}. Expected 5 parts.")

    trigger = CronTrigger(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
        timezone="UTC",
    )

    async def _run_scheduled_pipeline():
        from app.scheduler.jobs import execute_scheduled_pipeline

        await execute_scheduled_pipeline(job_id, story_id, framework)

    scheduler.add_job(
        _run_scheduled_pipeline,
        trigger=trigger,
        id=job_id,
        replace_existing=True,
        name=f"Pipeline: {story_id} ({framework})",
    )
    logger.info("job_added", job_id=job_id, cron=cron_expression, story_id=story_id)


def remove_job(job_id: str) -> bool:
    """Remove a scheduled job."""
    scheduler = get_scheduler()
    try:
        scheduler.remove_job(job_id)
        logger.info("job_removed", job_id=job_id)
        return True
    except Exception:
        return False


def pause_job(job_id: str) -> bool:
    """Pause a scheduled job."""
    scheduler = get_scheduler()
    try:
        scheduler.pause_job(job_id)
        return True
    except Exception:
        return False


def resume_job(job_id: str) -> bool:
    """Resume a paused job."""
    scheduler = get_scheduler()
    try:
        scheduler.resume_job(job_id)
        return True
    except Exception:
        return False


def list_jobs() -> list[dict]:
    """List all registered jobs with their next run time."""
    scheduler = get_scheduler()
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "pending": job.pending,
        })
    return jobs


def get_next_run_time(job_id: str) -> datetime | None:
    """Get the next scheduled run time for a job."""
    scheduler = get_scheduler()
    job = scheduler.get_job(job_id)
    return job.next_run_time if job else None
