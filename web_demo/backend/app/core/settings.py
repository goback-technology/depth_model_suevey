from __future__ import annotations

from pathlib import Path

WEB_DEMO_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = WEB_DEMO_DIR / "backend" / "data"
JOBS_DIR = DATA_DIR / "jobs"

JOBS_DIR.mkdir(parents=True, exist_ok=True)
