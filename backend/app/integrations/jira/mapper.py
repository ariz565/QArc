"""Jira mapper — convert between Jira API format and internal models."""

from __future__ import annotations

from typing import Any

from app.models.stories import JiraStory

import structlog

logger = structlog.get_logger()


def jira_issue_to_story(issue: dict[str, Any]) -> JiraStory:
    """
    Convert a Jira REST API issue into our JiraStory model.

    Handles both Jira Cloud (ADF) and Jira Server (wiki markup) description formats.
    """
    fields = issue.get("fields", {})

    # Extract description (ADF → plain text)
    description = _extract_description(fields.get("description"))

    # Extract priority
    priority_obj = fields.get("priority", {})
    priority_name = priority_obj.get("name", "Medium") if priority_obj else "Medium"
    priority = _normalize_priority(priority_name)

    # Extract labels
    labels = fields.get("labels", [])

    # Extract acceptance criteria from custom field or description
    acceptance = _extract_acceptance(description, fields)

    # Extract story points
    story_points = int(fields.get("story_points") or fields.get("customfield_10016") or 0)

    # Extract sprint
    sprint = _extract_sprint(fields)

    return JiraStory(
        id=issue.get("key", ""),
        title=fields.get("summary", "Untitled Story"),
        description=description,
        priority=priority,
        labels=labels,
        acceptance=acceptance,
        story_points=story_points,
        sprint=sprint,
    )


def story_to_jira_bug(
    title: str,
    description: str,
    severity: str,
    steps: list[str],
    expected: str,
    actual: str,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """Convert a bug report into Jira issue create payload."""
    priority_map = {
        "critical": "Highest",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }

    steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))

    description_adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": description}],
            },
            {
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Steps to Reproduce"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": steps_text}],
            },
            {
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Expected Result"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": expected}],
            },
            {
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Actual Result"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": actual}],
            },
        ],
    }

    return {
        "summary": title,
        "description": description_adf,
        "issuetype": {"name": "Bug"},
        "priority": {"name": priority_map.get(severity, "Medium")},
        "labels": labels or ["qa-nexus", "auto-reported"],
    }


def _extract_description(desc: Any) -> str:
    """Extract plain text from Jira ADF or string description."""
    if desc is None:
        return ""
    if isinstance(desc, str):
        return desc

    # ADF format
    if isinstance(desc, dict) and desc.get("type") == "doc":
        parts: list[str] = []
        for block in desc.get("content", []):
            for inline in block.get("content", []):
                if inline.get("type") == "text":
                    parts.append(inline.get("text", ""))
        return "\n".join(parts)

    return str(desc)


def _normalize_priority(jira_priority: str) -> str:
    """Normalize Jira priority to our model's allowed values."""
    mapping = {
        "highest": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Medium",
        "lowest": "Medium",
    }
    return mapping.get(jira_priority.lower(), "Medium")


def _extract_acceptance(description: str, fields: dict) -> list[str]:
    """Extract acceptance criteria from description or custom field."""
    # Check for common custom field names
    for field_key in ["customfield_10100", "customfield_10101", "acceptance_criteria"]:
        val = fields.get(field_key)
        if val and isinstance(val, str):
            return [line.strip("- •").strip() for line in val.split("\n") if line.strip()]

    # Try to extract from description
    import re

    match = re.search(
        r"[Aa]cceptance [Cc]riteria[:\s]*\n([\s\S]*?)(?:\n\n|\Z)",
        description,
    )
    if match:
        lines = match.group(1).strip().split("\n")
        return [line.strip("- •*").strip() for line in lines if line.strip()]

    return []


def _extract_sprint(fields: dict) -> str:
    """Extract sprint name from Jira sprint field."""
    sprint_data = fields.get("sprint") or fields.get("customfield_10020")
    if isinstance(sprint_data, dict):
        return sprint_data.get("name", "")
    if isinstance(sprint_data, list) and sprint_data:
        last_sprint = sprint_data[-1]
        if isinstance(last_sprint, dict):
            return last_sprint.get("name", "")
        if isinstance(last_sprint, str):
            import re

            match = re.search(r"name=([^,]+)", last_sprint)
            return match.group(1) if match else ""
    return ""
