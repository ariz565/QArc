"""Abstract test runner — all framework runners inherit this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RunResult:
    """Result from a single test runner execution."""

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    report_path: Path | None = None  # Path to JUnit XML or JSON report
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    artifacts: list[Path] = field(default_factory=list)  # Screenshots, videos, traces


class BaseRunner(ABC):
    """Abstract interface for running generated test suites."""

    framework_id: str = ""
    framework_name: str = ""

    @abstractmethod
    async def setup(self, workspace: Path) -> None:
        """Install framework dependencies in the workspace."""
        ...

    @abstractmethod
    async def run(
        self,
        workspace: Path,
        test_file: str,
        *,
        headless: bool = True,
        timeout_ms: int = 30000,
        retries: int = 0,
    ) -> RunResult:
        """Execute test file and return results."""
        ...

    @abstractmethod
    async def cleanup(self, workspace: Path) -> None:
        """Clean up temporary files after execution."""
        ...
