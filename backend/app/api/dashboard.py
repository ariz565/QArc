"""Dashboard routes — stats and trends."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.dashboard import DashboardStats, WeeklyTrend
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats() -> DashboardStats:
    """Get aggregated dashboard statistics."""
    return dashboard_service.get_stats()


@router.get("/weekly-trend", response_model=WeeklyTrend)
async def get_weekly_trend() -> WeeklyTrend:
    """Get weekly test trend data."""
    return dashboard_service.get_weekly_trend()
