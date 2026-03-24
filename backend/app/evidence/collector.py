"""Evidence collector — gather screenshots, videos, traces from test sandbox."""

from __future__ import annotations

import mimetypes
from pathlib import Path

import structlog

from app.models.artifacts import Artifact

logger = structlog.get_logger()


class EvidenceCollector:
    """
    Collects test execution artifacts (screenshots, videos, traces)
    from the sandbox workspace and prepares them for storage.
    """

    # Known artifact file patterns
    SCREENSHOT_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
    VIDEO_EXTS = {".webm", ".mp4"}
    TRACE_EXTS = {".zip"}  # Playwright traces
    LOG_EXTS = {".log", ".txt"}
    REPORT_EXTS = {".html", ".xml", ".json"}

    def collect_from_workspace(
        self, workspace: Path, execution_id: str
    ) -> list[Artifact]:
        """
        Scan a test sandbox workspace for artifact files.

        Looks in:
        - artifacts/  (Playwright output)
        - results/    (reports)
        - test-results/  (Playwright default)
        """
        artifacts: list[Artifact] = []

        search_dirs = [
            workspace / "artifacts",
            workspace / "results",
            workspace / "test-results",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for file_path in search_dir.rglob("*"):
                if not file_path.is_file():
                    continue

                artifact_type = self._classify(file_path)
                mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

                artifact = Artifact(
                    execution_id=execution_id,
                    type=artifact_type,
                    file_path=str(file_path),
                    file_name=file_path.name,
                    mime_type=mime,
                    size_bytes=file_path.stat().st_size,
                )
                artifacts.append(artifact)

        logger.info(
            "evidence_collected",
            execution_id=execution_id,
            count=len(artifacts),
            types=[a.type for a in artifacts],
        )
        return artifacts

    def collect_screenshots(self, workspace: Path, execution_id: str) -> list[Artifact]:
        """Collect only screenshots."""
        all_artifacts = self.collect_from_workspace(workspace, execution_id)
        return [a for a in all_artifacts if a.type == "screenshot"]

    def collect_videos(self, workspace: Path, execution_id: str) -> list[Artifact]:
        """Collect only videos."""
        all_artifacts = self.collect_from_workspace(workspace, execution_id)
        return [a for a in all_artifacts if a.type == "video"]

    def _classify(self, path: Path) -> str:
        """Classify artifact type by file extension."""
        ext = path.suffix.lower()

        if ext in self.SCREENSHOT_EXTS:
            return "screenshot"
        if ext in self.VIDEO_EXTS:
            return "video"
        if ext in self.TRACE_EXTS:
            return "trace"
        if ext in self.LOG_EXTS:
            return "log"
        if ext in self.REPORT_EXTS:
            return "report"
        return "other"
