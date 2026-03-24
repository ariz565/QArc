"""Execution history routes."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.executions import ExecutionListResponse, ExecutionRun
from app.services import execution_service

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("", response_model=ExecutionListResponse)
async def list_executions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    story_id: str | None = None,
) -> ExecutionListResponse:
    """List execution history with pagination and filtering."""
    runs, total = execution_service.list_executions(limit, offset, story_id)
    return ExecutionListResponse(executions=runs, total=total)


@router.get("/{execution_id}", response_model=ExecutionRun)
async def get_execution(execution_id: str) -> ExecutionRun:
    """Get a single execution run by ID."""
    run = execution_service.get_execution(execution_id)
    if not run:
        from app.core import QANexusError
        raise QANexusError(f"Execution '{execution_id}' not found", 404)
    return run
