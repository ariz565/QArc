"""FastAPI dependency injection — shared resources available to all routes."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, settings
from app.db import async_session


def get_settings() -> Settings:
    """Inject application settings."""
    return settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Inject an async database session (auto-closes on exit)."""
    async with async_session() as session:
        yield session
