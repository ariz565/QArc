"""Jira API — import stories and health-check."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.integrations.jira.client import JiraClient
from app.integrations.jira.mapper import jira_issue_to_story

router = APIRouter(prefix="/jira", tags=["jira"])


def _client() -> JiraClient:
    return JiraClient(
        base_url=settings.jira_base_url,
        email=settings.jira_email,
        api_token=settings.jira_api_token,
    )


@router.get("/health")
async def jira_health() -> dict:
    """Check Jira connectivity."""
    client = _client()
    ok, message = await client.health_check()
    return {"connected": ok, "message": message}


@router.get("/stories/{issue_key}")
async def get_story(issue_key: str) -> dict:
    """Fetch a single Jira issue and convert to story model."""
    client = _client()
    issue = await client.get_issue(issue_key)
    story = jira_issue_to_story(issue)
    return story.model_dump()


@router.get("/sprint-stories")
async def sprint_stories(project_key: str, sprint_name: str) -> list[dict]:
    """Import stories from a Jira sprint by project key and sprint name."""
    client = _client()
    issues = await client.get_sprint_stories(project_key, sprint_name)
    return [jira_issue_to_story(i).model_dump() for i in issues]


@router.post("/search")
async def search_issues(jql: str, max_results: int = 50) -> list[dict]:
    """Run a JQL query and return stories."""
    client = _client()
    issues = await client.search_issues(jql, max_results=max_results)
    return [jira_issue_to_story(i).model_dump() for i in issues]
