"""Bugs API — view and manage generated bug reports."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db import async_session
from app.db.repositories.bug_repo import BugRepository
from app.models.bugs import BugReport

router = APIRouter(prefix="/bugs", tags=["bugs"])


# ── Static paths BEFORE path parameters (FastAPI matches top-down) ──

@router.get("/open", response_model=list[BugReport])
async def list_open_bugs() -> list[BugReport]:
    """List all open (unfiled) bug reports."""
    async with async_session() as session:
        repo = BugRepository(session)
        return await repo.list_open()


@router.get("/detail/{bug_id}", response_model=BugReport)
async def get_bug(bug_id: str) -> BugReport:
    """Get a single bug report."""
    async with async_session() as session:
        repo = BugRepository(session)
        bug = await repo.get(bug_id)
        if not bug:
            raise HTTPException(status_code=404, detail=f"Bug '{bug_id}' not found")
        return bug


@router.get("/{execution_id}", response_model=list[BugReport])
async def list_bugs_for_execution(execution_id: str) -> list[BugReport]:
    """List all bug reports for an execution."""
    async with async_session() as session:
        repo = BugRepository(session)
        return await repo.get_by_execution(execution_id)


@router.post("/{bug_id}/file-to-jira")
async def file_bug_to_jira(bug_id: str) -> dict:
    """File a bug report to Jira."""
    async with async_session() as session:
        repo = BugRepository(session)
        bug = await repo.get(bug_id)
        if not bug:
            raise HTTPException(status_code=404, detail=f"Bug '{bug_id}' not found")

    from app.integrations.jira.bug_reporter import JiraBugReporter

    reporter = JiraBugReporter()
    jira_key = await reporter.report_bug(bug)

    if jira_key:
        async with async_session() as session:
            repo = BugRepository(session)
            await repo.update_jira_key(bug_id, jira_key)
        return {"filed": True, "jira_key": jira_key}

    return {"filed": False, "reason": "Jira not configured or failed"}
