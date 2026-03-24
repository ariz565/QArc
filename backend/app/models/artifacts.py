"""Artifact models."""

from __future__ import annotations

from pydantic import BaseModel


class Artifact(BaseModel):
    id: int | None = None
    execution_id: str
    test_case_id: str | None = None
    type: str  # screenshot | video | trace | log | report
    file_path: str
    file_name: str
    mime_type: str = "application/octet-stream"
    size_bytes: int = 0
