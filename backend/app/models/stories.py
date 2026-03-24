"""Story schemas — maps to frontend JiraStory interface."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class JiraStory(BaseModel):
    id: str
    title: str
    description: str
    priority: Literal["Critical", "High", "Medium"]
    labels: list[str]
    acceptance: list[str]
    story_points: int
    sprint: str

    class Config:
        populate_by_name = True


class StoryBrief(BaseModel):
    """Lightweight story reference for dropdowns / selectors."""

    id: str
    title: str
    priority: Literal["Critical", "High", "Medium"]
