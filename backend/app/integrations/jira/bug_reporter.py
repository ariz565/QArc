"""Jira bug reporter — file bugs back to Jira from pipeline results."""

from __future__ import annotations

import structlog

from app.integrations.jira.client import JiraClient
from app.integrations.jira.mapper import story_to_jira_bug
from app.models.bugs import BugReport

logger = structlog.get_logger()


class JiraBugReporter:
    """Automatically file bug reports to Jira from test failures."""

    def __init__(self, client: JiraClient | None = None, project_key: str = ""):
        from app.config import settings

        self.client = client or JiraClient()
        self.project_key = project_key or settings.jira_project_key

    async def report_bug(self, bug: BugReport) -> str | None:
        """
        File a single bug to Jira. Returns the Jira issue key (e.g., PROJ-123).
        Returns None if Jira is not configured.
        """
        if not self.client.is_configured:
            logger.info("jira_skip_not_configured")
            return None

        issue_data = story_to_jira_bug(
            title=bug.title,
            description=bug.description,
            severity=bug.severity,
            steps=bug.steps_to_reproduce,
            expected=bug.expected_result,
            actual=bug.actual_result,
        )

        try:
            result = await self.client.create_issue(self.project_key, issue_data)
            jira_key = result.get("key", "")
            logger.info("bug_filed_to_jira", jira_key=jira_key, bug_id=bug.id)
            return jira_key
        except Exception as e:
            logger.error("jira_bug_report_failed", bug_id=bug.id, error=str(e))
            return None

    async def report_batch(self, bugs: list[BugReport]) -> dict[str, str | None]:
        """File multiple bugs. Returns {bug_id: jira_key}."""
        results = {}
        for bug in bugs:
            jira_key = await self.report_bug(bug)
            results[bug.id] = jira_key
        return results

    async def add_test_results_comment(
        self, issue_key: str, execution_id: str, passed: int, failed: int, coverage: float
    ) -> None:
        """Add a comment to the original story with test results summary."""
        if not self.client.is_configured:
            return

        comment = (
            f"🤖 QA Nexus Automated Test Results\n"
            f"─────────────────────────────\n"
            f"Execution: {execution_id}\n"
            f"Passed: {passed} | Failed: {failed}\n"
            f"Coverage: {coverage}%\n"
            f"{'✅ All tests passed!' if failed == 0 else '❌ Some tests failed — see bug reports.'}"
        )

        try:
            await self.client.add_comment(issue_key, comment)
            logger.info("jira_comment_added", issue_key=issue_key)
        except Exception as e:
            logger.error("jira_comment_failed", issue_key=issue_key, error=str(e))
