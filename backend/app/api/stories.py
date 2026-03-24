"""Story routes — CRUD for Jira stories."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.stories import JiraStory, StoryBrief
from app.services import story_service

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=list[JiraStory])
async def list_stories() -> list[JiraStory]:
    """Get all available stories."""
    return story_service.list_stories()


@router.get("/brief", response_model=list[StoryBrief])
async def list_stories_brief() -> list[StoryBrief]:
    """Get lightweight story list (for dropdowns)."""
    stories = story_service.list_stories()
    return [StoryBrief(id=s.id, title=s.title, priority=s.priority) for s in stories]


@router.get("/{story_id}", response_model=JiraStory)
async def get_story(story_id: str) -> JiraStory:
    """Get a single story by ID."""
    return story_service.get_story(story_id)


@router.post("", response_model=JiraStory, status_code=201)
async def create_story(story: JiraStory) -> JiraStory:
    """Create a new story."""
    return story_service.create_story(story)
