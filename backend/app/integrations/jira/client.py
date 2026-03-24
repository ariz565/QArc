"""Jira REST API client — async httpx-based client for Jira Cloud/Server.

Best practices (from httpx docs):
  - Reuse a SINGLE httpx.AsyncClient for connection pooling
  - Use fine-grained timeouts (connect vs read)
  - Properly close client via async context manager or aclose()
  - Use raise_for_status() for error propagation
"""

from __future__ import annotations

import base64
from typing import Any

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()

# Shared timeout config — generous read for Jira slowness, tight connect
_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class JiraClient:
    """
    Async Jira REST API client.

    Supports both Jira Cloud (email + API token) and Jira Server (PAT).
    Reuses a single httpx.AsyncClient for connection pooling.
    """

    def __init__(
        self,
        base_url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
    ):
        self.base_url = (base_url or settings.jira_base_url).rstrip("/")
        self._email = email or settings.jira_email
        self._token = api_token or settings.jira_api_token
        self._headers = {
            **self._build_auth(),
            "Content-Type": "application/json",
        }
        self._client: httpx.AsyncClient | None = None

    def _build_auth(self) -> dict[str, str]:
        if self._email and self._token:
            cred = base64.b64encode(f"{self._email}:{self._token}".encode()).decode()
            return {"Authorization": f"Basic {cred}"}
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self._token)

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazily create and reuse a single httpx.AsyncClient."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._headers,
                timeout=_TIMEOUT,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_issue(self, issue_key: str) -> dict[str, Any]:
        """Fetch a single Jira issue by key (e.g., PROJ-1042)."""
        client = await self._get_client()
        resp = await client.get(f"/rest/api/3/issue/{issue_key}")
        resp.raise_for_status()
        return resp.json()

    async def search_issues(self, jql: str, max_results: int = 50) -> list[dict[str, Any]]:
        """Search issues using JQL."""
        client = await self._get_client()
        resp = await client.get(
            "/rest/api/3/search",
            params={"jql": jql, "maxResults": max_results},
        )
        resp.raise_for_status()
        return resp.json().get("issues", [])

    async def get_sprint_stories(self, project_key: str, sprint_name: str) -> list[dict[str, Any]]:
        """Get all stories in a specific sprint."""
        jql = f'project = "{project_key}" AND sprint = "{sprint_name}" AND issuetype = Story'
        return await self.search_issues(jql)

    async def create_issue(self, project_key: str, issue_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new Jira issue (used for filing bugs)."""
        client = await self._get_client()
        payload = {
            "fields": {
                "project": {"key": project_key},
                **issue_data,
            }
        }
        resp = await client.post("/rest/api/3/issue", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def add_comment(self, issue_key: str, body: str) -> dict[str, Any]:
        """Add a comment to an existing issue."""
        client = await self._get_client()
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": body}],
                    }
                ],
            }
        }
        resp = await client.post(f"/rest/api/3/issue/{issue_key}/comment", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        """Move issue to a different status (e.g., 'In Progress', 'Done')."""
        client = await self._get_client()
        url = f"/rest/api/3/issue/{issue_key}/transitions"

        # Get available transitions
        resp = await client.get(url)
        resp.raise_for_status()
        transitions = resp.json().get("transitions", [])

        target = next((t for t in transitions if t["name"].lower() == transition_name.lower()), None)
        if not target:
            logger.warning("transition_not_found", issue=issue_key, transition=transition_name)
            return False

        # Apply transition (reuse same client connection)
        resp = await client.post(url, json={"transition": {"id": target["id"]}})
        resp.raise_for_status()
        return True

    async def health_check(self) -> tuple[bool, str]:
        """Check Jira connectivity. Returns (is_healthy, message)."""
        if not self.is_configured:
            return False, "Jira not configured"
        try:
            client = await self._get_client()
            resp = await client.get("/rest/api/3/myself")
            if resp.status_code == 200:
                user = resp.json()
                return True, f"Connected as {user.get('displayName', 'Unknown')}"
            return False, f"HTTP {resp.status_code}"
        except Exception as e:
            return False, str(e)
