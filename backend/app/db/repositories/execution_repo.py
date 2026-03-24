"""Execution repository — CRUD for executions table."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables import ExecutionRow
from app.models.executions import ExecutionRun
from app.orchestrator.state import PipelineState


class ExecutionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_from_state(self, state: PipelineState, story_title: str) -> ExecutionRun:
        """Persist completed pipeline state as an execution record."""
        row = ExecutionRow(
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
            agent_outputs=state.outputs,
            error=state.error,
        )
        self.session.add(row)
        await self.session.commit()
        return self._to_model(row)

    async def save_run(self, run: ExecutionRun) -> ExecutionRun:
        """Persist an ExecutionRun directly."""
        row = ExecutionRow(
            id=run.id,
            story_id=run.story_id,
            story_title=run.story_title,
            framework=run.framework,
            trigger=run.trigger,
            status=run.status,
            started_at=run.started_at,
            completed_at=run.completed_at,
            duration_ms=run.duration_ms,
            total_tests=run.total_tests,
            passed=run.passed,
            failed=run.failed,
            skipped=run.skipped,
            coverage=run.coverage,
            verdict=run.verdict,
        )
        merged = await self.session.merge(row)
        await self.session.commit()
        return self._to_model(merged)

    async def get(self, execution_id: str) -> ExecutionRun | None:
        row = await self.session.get(ExecutionRow, execution_id)
        return self._to_model(row) if row else None

    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        story_id: str | None = None,
    ) -> tuple[list[ExecutionRun], int]:
        q = select(ExecutionRow)
        if story_id:
            q = q.where(ExecutionRow.story_id == story_id)
        q = q.order_by(ExecutionRow.started_at.desc())

        # Count
        count_q = select(func.count()).select_from(ExecutionRow)
        if story_id:
            count_q = count_q.where(ExecutionRow.story_id == story_id)
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0

        # Page
        q = q.offset(offset).limit(limit)
        result = await self.session.execute(q)
        runs = [self._to_model(r) for r in result.scalars().all()]
        return runs, total

    async def get_agent_outputs(self, execution_id: str) -> dict[str, str]:
        """Get the raw agent outputs for an execution."""
        row = await self.session.get(ExecutionRow, execution_id)
        return row.agent_outputs if row else {}

    async def update_status(self, execution_id: str, status: str) -> None:
        row = await self.session.get(ExecutionRow, execution_id)
        if row:
            row.status = status
            if status in ("completed", "failed"):
                row.completed_at = datetime.now(timezone.utc)
            await self.session.commit()

    @staticmethod
    def _to_model(row: ExecutionRow) -> ExecutionRun:
        return ExecutionRun(
            id=row.id,
            story_id=row.story_id,
            story_title=row.story_title,
            framework=row.framework,
            trigger=row.trigger,
            status=row.status,
            started_at=row.started_at,
            completed_at=row.completed_at,
            duration_ms=row.duration_ms,
            total_tests=row.total_tests,
            passed=row.passed,
            failed=row.failed,
            skipped=row.skipped,
            coverage=row.coverage,
            verdict=row.verdict,
        )
