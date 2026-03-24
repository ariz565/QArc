"""Artifacts API — view and download test execution artifacts."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.evidence.storage import ArtifactStorage
from app.models.artifacts import Artifact
from app.db import async_session
from app.db.repositories.artifact_repo import ArtifactRepository

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

_storage = ArtifactStorage()


@router.get("/{execution_id}", response_model=list[Artifact])
async def list_artifacts(execution_id: str) -> list[Artifact]:
    """List all artifacts for an execution."""
    async with async_session() as session:
        repo = ArtifactRepository(session)
        return await repo.get_by_execution(execution_id)


@router.get("/{execution_id}/files")
async def list_artifact_files(execution_id: str) -> list[dict[str, str]]:
    """List artifact files on disk for an execution."""
    return _storage.list_for_execution(execution_id)


@router.get("/{execution_id}/download/{filename}")
async def download_artifact(execution_id: str, filename: str, artifact_type: str = "screenshot"):
    """Download a specific artifact file."""
    path = _storage.get_path(execution_id, artifact_type, filename)
    if not path or not path.exists():
        from app.core import QANexusError
        raise QANexusError(f"Artifact '{filename}' not found", 404)

    return FileResponse(
        path=str(path),
        filename=filename,
        media_type="application/octet-stream",
    )


@router.delete("/{execution_id}")
async def cleanup_artifacts(execution_id: str) -> dict:
    """Remove all stored artifacts for an execution."""
    _storage.cleanup_execution(execution_id)
    return {"cleaned": True, "execution_id": execution_id}
