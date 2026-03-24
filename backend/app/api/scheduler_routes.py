"""Scheduler API — manage cron-based pipeline triggers."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException
import structlog

from app.db import async_session
from app.db.repositories.schedule_repo import ScheduleRepository
from app.models.scheduler import CreateScheduledJobRequest, ScheduledJob, ToggleJobRequest
from app.scheduler.scheduler import (
    add_pipeline_job,
    get_next_run_time,
    list_jobs,
    remove_job,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/jobs", response_model=list[ScheduledJob])
async def get_scheduled_jobs() -> list[ScheduledJob]:
    """List all scheduled pipeline jobs."""
    async with async_session() as session:
        repo = ScheduleRepository(session)
        return await repo.list_all()


@router.post("/jobs", response_model=ScheduledJob, status_code=201)
async def create_scheduled_job(request: CreateScheduledJobRequest) -> ScheduledJob:
    """Create a new scheduled pipeline job."""
    job_id = f"job-{uuid4().hex[:8]}"

    job = ScheduledJob(
        id=job_id,
        name=request.name,
        story_id=request.story_id,
        framework=request.framework,
        cron_expression=request.cron_expression,
        enabled=True,
    )

    # Save to DB
    async with async_session() as session:
        repo = ScheduleRepository(session)
        await repo.create(job)

    # Register with APScheduler
    add_pipeline_job(
        job_id=job_id,
        cron_expression=request.cron_expression,
        story_id=request.story_id,
        framework=request.framework,
    )

    # Update next run time
    next_run = get_next_run_time(job_id)
    if next_run:
        job = job.model_copy(update={"next_run_at": next_run})

    logger.info("scheduled_job_created", job_id=job_id, cron=request.cron_expression)
    return job


@router.patch("/jobs/{job_id}", response_model=ScheduledJob)
async def toggle_job(job_id: str, request: ToggleJobRequest) -> ScheduledJob:
    """Enable or disable a scheduled job."""
    async with async_session() as session:
        repo = ScheduleRepository(session)
        job = await repo.toggle(job_id, request.enabled)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    if request.enabled:
        from app.scheduler.scheduler import resume_job
        resume_job(job_id)
    else:
        from app.scheduler.scheduler import pause_job
        pause_job(job_id)

    return job


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str) -> dict:
    """Delete a scheduled job."""
    # Remove from scheduler
    remove_job(job_id)

    # Remove from DB
    async with async_session() as session:
        repo = ScheduleRepository(session)
        deleted = await repo.delete(job_id)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return {"deleted": True, "job_id": job_id}


@router.get("/status")
async def scheduler_status() -> dict:
    """Get scheduler health status."""
    jobs = list_jobs()
    return {
        "running": True,
        "total_jobs": len(jobs),
        "jobs": jobs,
    }
