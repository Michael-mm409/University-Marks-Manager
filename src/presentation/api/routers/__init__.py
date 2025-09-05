"""Aggregate API routers for presentation layer.

Importing the modules ensures Pylint can resolve the attribute instead of
attempting to find a top-level symbol during the "from X import router" form.
"""
from __future__ import annotations

from fastapi import APIRouter

from . import semesters as _semesters_mod  # noqa: F401
from . import subjects as _subjects_mod  # noqa: F401
from . import assignments as _assignments_mod  # noqa: F401
from . import exams as _exams_mod  # noqa: F401

api_router = APIRouter(prefix="/api", tags=["api"])
api_router.include_router(_semesters_mod.router)
api_router.include_router(_subjects_mod.router)
api_router.include_router(_assignments_mod.router)
api_router.include_router(_exams_mod.router)

__all__ = ["api_router"]
