from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.settings import JOBS_DIR
from app.schemas.job import Job, JobCreateResponse
from app.services.pipeline import run_job
from app.services.store import job_store

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("", response_model=JobCreateResponse)
async def create_job(
    image: UploadFile = File(...),
    model: str = Form("Small"),
    mesh_method: str = Form("poisson"),
    voxel_size: float = Form(0.03),
    depth_trunc: float = Form(2.2),
) -> JobCreateResponse:
    if model not in {"Small", "Base", "Large"}:
        raise HTTPException(status_code=400, detail="model must be one of Small/Base/Large")
    if mesh_method not in {"poisson", "bpa"}:
        raise HTTPException(status_code=400, detail="mesh_method must be one of poisson/bpa")
    if not (0.005 <= voxel_size <= 0.2):
        raise HTTPException(status_code=400, detail="voxel_size must be between 0.005 and 0.2")
    if not (0.3 <= depth_trunc <= 20.0):
        raise HTTPException(status_code=400, detail="depth_trunc must be between 0.3 and 20.0")

    job_id = str(uuid.uuid4())
    await job_store.create(job_id)

    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(image.filename or "input.jpg").suffix or ".jpg"
    input_path = job_dir / f"input{ext}"

    body = await image.read()
    if len(body) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="image is too large (max 10MB)")

    input_path.write_bytes(body)

    asyncio.create_task(
        run_job(
            job_id,
            input_path,
            job_dir,
            model=model,
            mesh_method=mesh_method,
            voxel_size=voxel_size,
            depth_trunc=depth_trunc,
        )
    )

    return JobCreateResponse(job_id=job_id, status="queued")


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str) -> Job:
    job = await job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
