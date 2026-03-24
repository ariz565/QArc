"""Test case repository — CRUD for test_cases table."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables import TestCaseRow
from app.models.test_cases import TestCase


class TestCaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_batch(self, test_cases: list[TestCase], execution_id: str) -> None:
        """Bulk insert test cases for a pipeline run."""
        for tc in test_cases:
            row = TestCaseRow(
                id=tc.id,
                execution_id=execution_id,
                story_id=tc.story_id or "",
                name=tc.name,
                type=tc.type,
                priority=tc.priority,
                scenario=tc.scenario,
                steps=tc.steps,
                expected=tc.expected,
                status=tc.status,
                duration=tc.duration,
                automation_code=tc.automation_code,
            )
            self.session.add(row)
        await self.session.commit()

    async def get_by_execution(self, execution_id: str) -> list[TestCase]:
        q = select(TestCaseRow).where(TestCaseRow.execution_id == execution_id)
        result = await self.session.execute(q)
        return [self._to_model(r) for r in result.scalars().all()]

    async def get_by_story(self, story_id: str) -> list[TestCase]:
        q = select(TestCaseRow).where(TestCaseRow.story_id == story_id)
        result = await self.session.execute(q)
        return [self._to_model(r) for r in result.scalars().all()]

    async def update_status(self, test_case_id: str, status: str, duration: str | None = None) -> None:
        row = await self.session.get(TestCaseRow, test_case_id)
        if row:
            row.status = status
            if duration:
                row.duration = duration
            await self.session.commit()

    @staticmethod
    def _to_model(row: TestCaseRow) -> TestCase:
        return TestCase(
            id=row.id,
            name=row.name,
            type=row.type,
            priority=row.priority,
            scenario=row.scenario,
            steps=row.steps,
            expected=row.expected,
            status=row.status,
            duration=row.duration,
            automation_code=row.automation_code,
            story_id=row.story_id,
        )
