"""Custom exceptions and FastAPI error handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class QANexusError(Exception):
    """Base exception for all QA Nexus errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ProviderNotFoundError(QANexusError):
    """Raised when a requested LLM provider is not registered."""

    def __init__(self, provider: str) -> None:
        super().__init__(f"LLM provider '{provider}' is not registered", 404)


class ProviderUnavailableError(QANexusError):
    """Raised when a provider's API is unreachable."""

    def __init__(self, provider: str, reason: str = "") -> None:
        detail = f": {reason}" if reason else ""
        super().__init__(f"LLM provider '{provider}' is unavailable{detail}", 503)


class AgentError(QANexusError):
    """Raised when an agent fails during execution."""

    def __init__(self, agent_id: str, reason: str) -> None:
        super().__init__(f"Agent '{agent_id}' failed: {reason}", 500)


class PipelineError(QANexusError):
    """Raised when the pipeline orchestrator encounters an error."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Pipeline error: {reason}", 500)


class StoryNotFoundError(QANexusError):
    """Raised when a requested story does not exist."""

    def __init__(self, story_id: str) -> None:
        super().__init__(f"Story '{story_id}' not found", 404)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach error handlers to the FastAPI app."""

    @app.exception_handler(QANexusError)
    async def handle_qa_nexus_error(_req: Request, exc: QANexusError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )
