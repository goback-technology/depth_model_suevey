from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.jobs import router as jobs_router
from app.core.settings import JOBS_DIR

API_VERSION = "0.1.1"

app = FastAPI(title="Depth Web Demo API", version=API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.mount("/artifacts", StaticFiles(directory=str(JOBS_DIR)), name="artifacts")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/version")
async def version() -> dict[str, str]:
    return {"version": API_VERSION}
