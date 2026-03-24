"""Bug report repository — CRUD for bug_reports table."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables import BugReportRow
from app.models.bugs import BugReport


class BugRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, bug: BugReport) -> BugReport:
        row = BugReportRow(
            id=bug.id,
            execution_id=bug.execution_id,
            test_case_id=bug.test_case_id,
            title=bug.title,
            severity=bug.severity,
            description=bug.description,
            steps_to_reproduce=bug.steps_to_reproduce,
            expected_result=bug.expected_result,
            actual_result=bug.actual_result,
            environment=bug.environment,
            jira_key=bug.jira_key,
            status=bug.status,
        )
        self.session.add(row)
        await self.session.commit()
        return bug

    async def save_batch(self, bugs: list[BugReport]) -> None:
        """Save multiple bugs in a single transaction."""
        rows = [
            BugReportRow(
                id=bug.id,
                execution_id=bug.execution_id,
                test_case_id=bug.test_case_id,
                title=bug.title,
                severity=bug.severity,
                description=bug.description,
                steps_to_reproduce=bug.steps_to_reproduce,
                expected_result=bug.expected_result,
                actual_result=bug.actual_result,
                environment=bug.environment,
                jira_key=bug.jira_key,
                status=bug.status,
            )
            for bug in bugs
        ]
        self.session.add_all(rows)
        await self.session.commit()

    async def get(self, bug_id: str) -> BugReport | None:
        row = await self.session.get(BugReportRow, bug_id)
        return self._to_model(row) if row else None

    async def get_by_execution(self, execution_id: str) -> list[BugReport]:
        q = select(BugReportRow).where(BugReportRow.execution_id == execution_id)
        result = await self.session.execute(q)
        return [self._to_model(r) for r in result.scalars().all()]

    async def update_jira_key(self, bug_id: str, jira_key: str) -> None:
        row = await self.session.get(BugReportRow, bug_id)
        if row:
            row.jira_key = jira_key
            row.status = "reported"
            await self.session.commit()

    async def list_open(self) -> list[BugReport]:
        q = select(BugReportRow).where(BugReportRow.status == "open")
        result = await self.session.execute(q)
        return [self._to_model(r) for r in result.scalars().all()]

    @staticmethod
    def _to_model(row: BugReportRow) -> BugReport:
        return BugReport(
            id=row.id,
            execution_id=row.execution_id,
            test_case_id=row.test_case_id,
            title=row.title,
            severity=row.severity,
            description=row.description,
            steps_to_reproduce=row.steps_to_reproduce,
            expected_result=row.expected_result,
            actual_result=row.actual_result,
            environment=row.environment,
            jira_key=row.jira_key,
            status=row.status,
        )
