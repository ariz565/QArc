"""Artifact storage — persist collected evidence files."""

from __future__ import annotations

import shutil
from pathlib import Path

import structlog

from app.config import settings
from app.models.artifacts import Artifact

logger = structlog.get_logger()


class ArtifactStorage:
    """
    File-based artifact storage.

    Stores artifacts in:
        {storage_root}/{execution_id}/{artifact_type}/{filename}
    """

    def __init__(self, storage_root: Path | None = None):
        self._root = storage_root or Path(settings.workspace_dir) / ".artifacts"
        self._root.mkdir(parents=True, exist_ok=True)

    def store(self, artifact: Artifact) -> Artifact:
        """
        Copy an artifact file from sandbox to persistent storage.
        Updates the artifact's file_path to the new location.
        """
        source = Path(artifact.file_path)
        if not source.exists():
            logger.warning("artifact_source_missing", path=str(source))
            return artifact

        dest_dir = self._root / artifact.execution_id / artifact.type
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / artifact.file_name

        shutil.copy2(str(source), str(dest))

        updated = artifact.model_copy(update={
            "file_path": str(dest),
            "size_bytes": dest.stat().st_size,
        })

        logger.info("artifact_stored", type=artifact.type, dest=str(dest))
        return updated

    def store_batch(self, artifacts: list[Artifact]) -> list[Artifact]:
        """Store multiple artifacts."""
        return [self.store(a) for a in artifacts]

    def get_path(self, execution_id: str, artifact_type: str, filename: str) -> Path | None:
        """Get the path to a stored artifact."""
        path = self._root / execution_id / artifact_type / filename
        return path if path.exists() else None

    def list_for_execution(self, execution_id: str) -> list[dict[str, str]]:
        """List all stored artifacts for an execution."""
        exec_dir = self._root / execution_id
        if not exec_dir.exists():
            return []

        files = []
        for f in exec_dir.rglob("*"):
            if f.is_file():
                files.append({
                    "path": str(f.relative_to(self._root)),
                    "name": f.name,
                    "type": f.parent.name,
                    "size": str(f.stat().st_size),
                })
        return files

    def cleanup_execution(self, execution_id: str) -> None:
        """Remove all stored artifacts for an execution."""
        exec_dir = self._root / execution_id
        if exec_dir.exists():
            shutil.rmtree(exec_dir, ignore_errors=True)

    @property
    def storage_root(self) -> Path:
        return self._root
