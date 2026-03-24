"""SQLAlchemy 2.0 async engine + session factory.

Uses settings.db_url for the connection string. Default:
  sqlite+aiosqlite:///data/qa_nexus.db (relative to backend/)
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

engine = create_async_engine(
    settings.db_url,
    echo=settings.app_env == "development",
    future=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables (called at app startup)."""
    from app.db.tables import Base  # noqa: F811

    # Ensure SQLite data dir exists
    if "sqlite" in settings.db_url:
        db_path = settings.db_url.split("///")[-1] if "///" in settings.db_url else ""
        if db_path:
            (_BASE_DIR / db_path).parent.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose engine (called at app shutdown)."""
    await engine.dispose()
