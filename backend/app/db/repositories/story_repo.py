"""Story repository — CRUD for stories table."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables import StoryRow
from app.models.stories import JiraStory


class StoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[JiraStory]:
        result = await self.session.execute(select(StoryRow).order_by(StoryRow.created_at.desc()))
        return [self._to_model(r) for r in result.scalars().all()]

    async def get(self, story_id: str) -> JiraStory | None:
        row = await self.session.get(StoryRow, story_id)
        return self._to_model(row) if row else None

    async def create(self, story: JiraStory, source: str = "manual") -> JiraStory:
        row = StoryRow(
            id=story.id,
            title=story.title,
            description=story.description,
            priority=story.priority,
            labels=story.labels,
            acceptance=story.acceptance,
            story_points=story.story_points,
            sprint=story.sprint,
            source=source,
        )
        self.session.add(row)
        await self.session.commit()
        return story

    async def update(self, story: JiraStory) -> JiraStory:
        row = await self.session.get(StoryRow, story.id)
        if row:
            row.title = story.title
            row.description = story.description
            row.priority = story.priority
            row.labels = story.labels
            row.acceptance = story.acceptance
            row.story_points = story.story_points
            row.sprint = story.sprint
            await self.session.commit()
        return story

    async def delete(self, story_id: str) -> bool:
        row = await self.session.get(StoryRow, story_id)
        if row:
            await self.session.delete(row)
            await self.session.commit()
            return True
        return False

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(StoryRow))
        return result.scalar_one()

    @staticmethod
    def _to_model(row: StoryRow) -> JiraStory:
        return JiraStory(
            id=row.id,
            title=row.title,
            description=row.description,
            priority=row.priority,
            labels=row.labels,
            acceptance=row.acceptance,
            story_points=row.story_points,
            sprint=row.sprint,
        )
