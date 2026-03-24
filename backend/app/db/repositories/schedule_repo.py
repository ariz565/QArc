"""Schedule repository — CRUD for scheduled_jobs table."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables import ScheduledJobRow
from app.models.scheduler import ScheduledJob


class ScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job: ScheduledJob) -> ScheduledJob:
        row = ScheduledJobRow(
            id=job.id,
            name=job.name,
            story_id=job.story_id,
            framework=job.framework,
            cron_expression=job.cron_expression,
            enabled=job.enabled,
        )
        self.session.add(row)
        await self.session.commit()
        return job

    async def get(self, job_id: str) -> ScheduledJob | None:
        row = await self.session.get(ScheduledJobRow, job_id)
        return self._to_model(row) if row else None

    async def list_all(self) -> list[ScheduledJob]:
        result = await self.session.execute(select(ScheduledJobRow))
        return [self._to_model(r) for r in result.scalars().all()]

    async def list_enabled(self) -> list[ScheduledJob]:
        q = select(ScheduledJobRow).where(ScheduledJobRow.enabled == True)  # noqa: E712
        result = await self.session.execute(q)
        return [self._to_model(r) for r in result.scalars().all()]

    async def update_last_run(self, job_id: str) -> None:
        row = await self.session.get(ScheduledJobRow, job_id)
        if row:
            row.last_run_at = datetime.now(timezone.utc)
            await self.session.commit()

    async def toggle(self, job_id: str, enabled: bool) -> ScheduledJob | None:
        row = await self.session.get(ScheduledJobRow, job_id)
        if row:
            row.enabled = enabled
            await self.session.commit()
            return self._to_model(row)
        return None

    async def delete(self, job_id: str) -> bool:
        row = await self.session.get(ScheduledJobRow, job_id)
        if row:
            await self.session.delete(row)
            await self.session.commit()
            return True
        return False

    @staticmethod
    def _to_model(row: ScheduledJobRow) -> ScheduledJob:
        return ScheduledJob(
            id=row.id,
            name=row.name,
            story_id=row.story_id,
            framework=row.framework,
            cron_expression=row.cron_expression,
            enabled=row.enabled,
            last_run_at=row.last_run_at,
            next_run_at=row.next_run_at,
        )
