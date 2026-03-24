"""Runner registry — maps framework IDs to runner instances."""

from __future__ import annotations

from app.runner.base import BaseRunner
from app.runner.playwright_runner import PlaywrightRunner
from app.runner.selenium_runner import SeleniumRunner

_runners: dict[str, BaseRunner] = {}


def initialize_runners(base_url: str = "http://localhost:3000") -> None:
    """Register all available test runners."""
    _runners["playwright"] = PlaywrightRunner(base_url=base_url)
    _runners["selenium"] = SeleniumRunner(base_url=base_url)


def get_runner(framework_id: str) -> BaseRunner | None:
    """Get runner for a framework. Returns None if not supported."""
    return _runners.get(framework_id)


def available_runners() -> list[str]:
    """List registered runner framework IDs."""
    return list(_runners.keys())
