"""Artifact repository — CRUD for artifacts table."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables import ArtifactRow
from app.models.artifacts import Artifact


class ArtifactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, artifact: Artifact) -> Artifact:
        row = ArtifactRow(
            execution_id=artifact.execution_id,
            test_case_id=artifact.test_case_id,
            type=artifact.type,
            file_path=artifact.file_path,
            file_name=artifact.file_name,
            mime_type=artifact.mime_type,
            size_bytes=artifact.size_bytes,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return artifact.model_copy(update={"id": row.id})

    async def get_by_execution(self, execution_id: str) -> list[Artifact]:
        q = select(ArtifactRow).where(ArtifactRow.execution_id == execution_id)
        result = await self.session.execute(q)
        return [self._to_model(r) for r in result.scalars().all()]

    async def get_by_test_case(self, test_case_id: str) -> list[Artifact]:
        q = select(ArtifactRow).where(ArtifactRow.test_case_id == test_case_id)
        result = await self.session.execute(q)
        return [self._to_model(r) for r in result.scalars().all()]

    @staticmethod
    def _to_model(row: ArtifactRow) -> Artifact:
        return Artifact(
            id=row.id,
            execution_id=row.execution_id,
            test_case_id=row.test_case_id,
            type=row.type,
            file_path=row.file_path,
            file_name=row.file_name,
            mime_type=row.mime_type,
            size_bytes=row.size_bytes,
        )
