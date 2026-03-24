"""CORS and request-logging middleware."""

from __future__ import annotations

import time

import structlog
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

logger = structlog.get_logger()


def register_middleware(app: FastAPI) -> None:
    """Attach all middleware to the FastAPI app."""

    # ── CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request logger ──
    @app.middleware("http")
    async def log_requests(request: Request, call_next) -> Response:  # noqa: ANN001
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            ms=round(elapsed, 1),
        )
        return response
