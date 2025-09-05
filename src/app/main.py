"""FastAPI entrypoint providing an HTMX + Jinja2 interface.

Run with:
    uvicorn src.fastapi_main:app --reload
"""
from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import SQLModel

# Local imports
from src.infrastructure.db.engine import engine
from src.presentation.api.routers import api_router as api
from src.presentation.web.views import views

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR.parent / "templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Application lifespan context.

    Startup: create tables (idempotent) and initialize Jinja2 environment.
    Shutdown: currently no actions (placeholder for future resource cleanup).
    """
    # Startup
    SQLModel.metadata.create_all(engine)
    fastapi_app.state.jinja_env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    yield
    # Shutdown (no-op)


APPLICATION = FastAPI(title="University Marks Manager API", lifespan=lifespan)


APPLICATION.include_router(api)
APPLICATION.include_router(views)

# Optionally serve static (tailwind compiled CSS could go here later)
static_dir = BASE_DIR.parent / "static"
static_dir.mkdir(exist_ok=True)
APPLICATION.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount original assets (icons) if present at repo root / assets
ROOT_DIR = BASE_DIR.parent
assets_dir = ROOT_DIR / "assets"
if assets_dir.exists():
    APPLICATION.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
app = APPLICATION  # backwards compatible name for uvicorn target

__all__ = ["app", "APPLICATION"]
