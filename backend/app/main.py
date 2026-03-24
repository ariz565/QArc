"""QA Nexus Backend — FastAPI Application Factory.

Modern FastAPI 2026 patterns:
  - Lifespan context manager (replaces on_event)
  - Pydantic Settings v2 (env-driven config)
  - Structured logging (structlog)
  - Async-first throughout
  - Provider registry initialization at startup
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.core import register_exception_handlers
from app.core.middleware import register_middleware
from app.db import close_db, init_db
from app.providers.registry import initialize_providers
from app.runner.registry import initialize_runners
from app.scheduler.scheduler import start_scheduler, stop_scheduler

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """App startup/shutdown lifecycle."""
    # ── Startup ──
    logger.info(
        "starting",
        env=settings.app_env,
        provider=settings.llm_default_provider,
        port=settings.app_port,
    )
    await init_db()
    initialize_providers()
    initialize_runners()
    await start_scheduler()
    logger.info("ready", docs="/docs")

    yield

    # ── Shutdown ──
    logger.info("shutting_down")
    await stop_scheduler()
    await close_db()


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""
    app = FastAPI(
        title="QA Nexus API",
        description="AI-Powered Multi-Agent Testing Pipeline",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router)

    # Health check at root
    @app.get("/health")
    async def health() -> dict:
        return {"status": "healthy", "version": "1.0.0"}

    return app


# ── App instance ──
app = create_app()
