"""API router aggregation (re-export).

Minimal form: reuse the aggregated `api_router` defined in `presentation.api.routers`.
This avoids direct symbol imports that triggered Pylint E0611.
"""
from __future__ import annotations

from .routers import api_router

__all__ = ["api_router"]
