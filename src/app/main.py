"""FastAPI entrypoint providing an HTMX + Jinja2 interface.

Run with:
    uvicorn src.fastapi_main:app --reload
"""
from __future__ import annotations

from pathlib import Path
import os
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware

# Local imports
from src.infrastructure.db import models  # noqa: F401
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
    # For development: drop and recreate tables on each startup
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    fastapi_app.state.jinja_env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    # Debug routes gating (off by default). Enable by setting ENABLE_DEBUG_ROUTES to a truthy value.
    fastapi_app.state.enable_debug_routes = str(os.getenv("ENABLE_DEBUG_ROUTES", "")).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    # Optional shared secret for debug endpoints: require token query param if set
    fastapi_app.state.debug_token = os.getenv("DEBUG_TOKEN")
    yield
    # Shutdown (no-op)


APPLICATION = FastAPI(title="University Marks Manager API", lifespan=lifespan)


APPLICATION.include_router(api, prefix="/api")
APPLICATION.include_router(views)

# Enable server-side sessions for lightweight state (e.g., selected course)
# NOTE: Replace the secret key with an environment variable for production use.
APPLICATION.add_middleware(
    SessionMiddleware,
    secret_key="dev-secret-change-me",
    same_site="lax",
)

# Optionally serve static (tailwind compiled CSS could go here later)
static_dir = BASE_DIR.parent / "static"
static_dir.mkdir(exist_ok=True)
APPLICATION.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount original assets (icons) if present at repo root / assets
# BASE_DIR = src/app -> repo root is two levels up
ROOT_DIR = BASE_DIR.parent.parent
assets_dir = ROOT_DIR / "assets"
if assets_dir.exists():
    APPLICATION.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# Explicit /favicon.ico for browsers requesting root path
static_favicon = static_dir / "images" / "favicon.ico"
assets_favicon = assets_dir / "favicon.ico"
if static_favicon.exists() or assets_favicon.exists():
    @APPLICATION.get("/favicon.ico")
    def favicon():
        path = str(static_favicon if static_favicon.exists() else assets_favicon)
        return FileResponse(path)
app = APPLICATION  # backwards compatible name for uvicorn target

__all__ = ["app", "APPLICATION"]

# Root-level health endpoint (does not depend on API router mounting)
@APPLICATION.get("/healthz")
def healthz():
    return {"status": "ok"}
