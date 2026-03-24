"""Files API — browse and download generated test files."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.files.manager import FileManager

router = APIRouter(prefix="/files", tags=["files"])

_manager = FileManager()


@router.get("/{story_id}")
async def list_story_files(story_id: str) -> list[dict[str, str]]:
    """List all generated files for a story."""
    return _manager.list_story_files(story_id)


@router.get("/{story_id}/content")
async def read_file(story_id: str, path: str) -> dict:
    """Read a generated file's content."""
    try:
        content = _manager.read_file(path)
        return {"path": path, "content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
