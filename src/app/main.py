"""FastAPI entrypoint providing an HTMX + Jinja2 interface.

Run with:
    uvicorn src.app.main:app --reload
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import os
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# Local imports
from src.infrastructure.db import models  # noqa: F401
from src.infrastructure.db.engine import engine
from src.presentation.api.routers import api_router as api
from src.presentation.web.views import views

BASE_DIR = Path(__file__).resolve().parent
# Repo root is two levels up from src/app
ROOT_DIR = BASE_DIR.parent.parent
TEMPLATES_DIR = BASE_DIR.parent / "templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env at repo root (safe in dev/local)
try:
    load_dotenv(dotenv_path=ROOT_DIR / ".env")
except Exception:
    # Proceed without .env if loading fails
    pass

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
    # Enable template auto-reload in development so Jinja picks up template changes without restarts
    fastapi_app.state.jinja_env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        auto_reload=True,
        cache_size=0,  # avoid template caching during active development
    )
    # Provide global template variables
    fastapi_app.state.jinja_env.globals.update(
        current_year=str(datetime.now().year),
        app_version=os.getenv("APP_VERSION", "dev"),
        env_name=os.getenv("ENV", "dev"),
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


# Configure API version prefix from environment (default: v1)
API_VERSION = os.getenv("API_VERSION", "v1").strip().lstrip("/") or "v1"
API_PREFIX = f"/api/{API_VERSION}"

APPLICATION.include_router(api, prefix=API_PREFIX)
APPLICATION.include_router(views)

# Enable server-side sessions for lightweight state (e.g., selected course)
# NOTE: Replace the secret key with an environment variable for production use.
session_secret = os.getenv("SESSION_SECRET_KEY")
if not session_secret:
    raise RuntimeError("SESSION_SECRET_KEY environment variable is required for SessionMiddleware")
APPLICATION.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    same_site="lax",
)

# Optionally serve static (tailwind compiled CSS could go here later)
static_dir = BASE_DIR.parent / "static"
static_dir.mkdir(exist_ok=True)
APPLICATION.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount original assets (icons) if present at repo root / assets
assets_dir = ROOT_DIR / "assets"
if assets_dir.exists():
    APPLICATION.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# Explicit /favicon.ico for browsers requesting root path
static_favicon = static_dir / "images" / "favicon.ico"
assets_favicon = assets_dir / "favicon.ico"
if static_favicon.exists() or assets_favicon.exists():
    @APPLICATION.get("/favicon.ico")
    def favicon():
        """
        Short description.

        Raises:
            Description.
        """
        path = str(static_favicon if static_favicon.exists() else assets_favicon)
        return FileResponse(path)
app = APPLICATION  # backwards compatible name for uvicorn target

__all__ = ["app", "APPLICATION"]

# Root-level health endpoint (does not depend on API router mounting)
@APPLICATION.get("/healthz")
def healthz():
    """
    Short description.

    Raises:
        Description.
    """
    return {"status": "ok"}

# Backward compatibility: redirect legacy /api and /api/* to versioned prefix
@APPLICATION.api_route("/api", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])  # type: ignore[arg-type]
async def api_root_redirect(request: Request) -> RedirectResponse:
    qs = ("?" + request.url.query) if request.url.query else ""
    return RedirectResponse(url=f"{API_PREFIX}{qs}", status_code=308)

@APPLICATION.api_route("/api/{full_path:path}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])  # type: ignore[arg-type]
async def api_legacy_redirect(full_path: str, request: Request) -> RedirectResponse:
    qs = ("?" + request.url.query) if request.url.query else ""
    return RedirectResponse(url=f"{API_PREFIX}/{full_path}{qs}", status_code=308)

