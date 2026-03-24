"""Main API router — aggregates all route modules under /api/v1."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.agents import router as agents_router
from app.api.artifacts import router as artifacts_router
from app.api.bugs import router as bugs_router
from app.api.dashboard import router as dashboard_router
from app.api.executions import router as executions_router
from app.api.files import router as files_router
from app.api.jira_routes import router as jira_router
from app.api.pipeline import router as pipeline_router
from app.api.reports import router as reports_router
from app.api.scheduler_routes import router as scheduler_router
from app.api.settings_routes import router as settings_router
from app.api.stories import router as stories_router
from app.api.webhooks import router as webhooks_router
from app.api.ws import router as ws_router

api_router = APIRouter(prefix="/api/v1")

# REST endpoints
api_router.include_router(pipeline_router)
api_router.include_router(stories_router)
api_router.include_router(agents_router)
api_router.include_router(dashboard_router)
api_router.include_router(executions_router)
api_router.include_router(reports_router)
api_router.include_router(settings_router)
api_router.include_router(artifacts_router)
api_router.include_router(bugs_router)
api_router.include_router(files_router)
api_router.include_router(jira_router)
api_router.include_router(scheduler_router)
api_router.include_router(webhooks_router)

# WebSocket (no prefix — ws:// paths at root)
api_router.include_router(ws_router)
