from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.schemas.job import Job, JobArtifacts, JobStatus


class JobStore:
    def __init__(self) -> None:
        self._items: dict[str, Job] = {}
        self._lock = asyncio.Lock()

    async def create(self, job_id: str) -> Job:
        async with self._lock:
            item = Job(job_id=job_id, status=JobStatus.queued)
            self._items[job_id] = item
            return item

    async def get(self, job_id: str) -> Job | None:
        async with self._lock:
            return self._items.get(job_id)

    async def update(
        self,
        job_id: str,
        *,
        status: JobStatus | None = None,
        message: str | None = None,
        artifacts: JobArtifacts | None = None,
    ) -> Job | None:
        async with self._lock:
            item = self._items.get(job_id)
            if item is None:
                return None
            if status is not None:
                item.status = status
            if message is not None:
                item.message = message
            if artifacts is not None:
                item.artifacts = artifacts
            item.updated_at = datetime.now(timezone.utc)
            self._items[job_id] = item
            return item


job_store = JobStore()
