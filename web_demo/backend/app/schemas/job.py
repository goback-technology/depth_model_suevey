from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class JobArtifacts(BaseModel):
    depth_color_url: str | None = None
    voxels_url: str | None = None
    point_cloud_url: str | None = None
    mesh_url: str | None = None
    mesh_obj_url: str | None = None


class Job(BaseModel):
    job_id: str
    status: JobStatus
    message: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    artifacts: JobArtifacts = Field(default_factory=JobArtifacts)


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus
