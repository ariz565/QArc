"""Test sandbox — isolated temp directory for running generated tests."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import structlog

logger = structlog.get_logger()


class TestSandbox:
    """
    Creates an isolated workspace directory for a single test run.

    Layout:
        {base_dir}/{execution_id}/
        ├── tests/           ← Generated test files go here
        ├── results/         ← JUnit XML, JSON reports
        ├── artifacts/       ← Screenshots, videos, traces
        └── node_modules/    ← (if npm install needed)
    """

    def __init__(self, base_dir: Path | None = None):
        self._base_dir = base_dir or Path(tempfile.gettempdir()) / "qa-nexus-sandboxes"
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def create(self, execution_id: str) -> Path:
        """Create and return workspace directory for an execution."""
        workspace = self._base_dir / execution_id
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "tests").mkdir(exist_ok=True)
        (workspace / "results").mkdir(exist_ok=True)
        (workspace / "artifacts").mkdir(exist_ok=True)
        logger.info("sandbox_created", path=str(workspace), execution_id=execution_id)
        return workspace

    def write_test_file(self, workspace: Path, filename: str, content: str) -> Path:
        """Write a test file into the sandbox tests/ directory."""
        test_path = workspace / "tests" / filename
        test_path.write_text(content, encoding="utf-8")
        logger.info("test_file_written", path=str(test_path), size=len(content))
        return test_path

    def write_config_file(self, workspace: Path, filename: str, content: str) -> Path:
        """Write a config file (playwright.config.ts, etc.) into the workspace root."""
        config_path = workspace / filename
        config_path.write_text(content, encoding="utf-8")
        return config_path

    def get_results_dir(self, workspace: Path) -> Path:
        return workspace / "results"

    def get_artifacts_dir(self, workspace: Path) -> Path:
        return workspace / "artifacts"

    def list_artifacts(self, workspace: Path) -> list[Path]:
        """List all artifact files (screenshots, videos, etc.)."""
        artifacts_dir = workspace / "artifacts"
        if not artifacts_dir.exists():
            return []
        return [f for f in artifacts_dir.rglob("*") if f.is_file()]

    def cleanup(self, execution_id: str) -> None:
        """Remove sandbox directory after execution."""
        workspace = self._base_dir / execution_id
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
            logger.info("sandbox_cleaned", execution_id=execution_id)

    def cleanup_old(self, max_age_hours: int = 24) -> int:
        """Remove sandboxes older than max_age_hours. Returns count removed."""
        import time

        cutoff = time.time() - (max_age_hours * 3600)
        removed = 0
        for entry in self._base_dir.iterdir():
            if entry.is_dir() and entry.stat().st_mtime < cutoff:
                shutil.rmtree(entry, ignore_errors=True)
                removed += 1
        if removed:
            logger.info("sandboxes_cleaned", count=removed, max_age_hours=max_age_hours)
        return removed
