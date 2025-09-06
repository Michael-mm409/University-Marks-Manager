"""HTML view routes rendering Jinja templates (spaces only)."""
from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from src.presentation.api.deps import get_session
from src.infrastructure.db.models import (
    Semester,
)
from .template_helpers import _render
from .assignment_views import assignment_router
from .exam_views import exam_router
from .semester_views import semester_router
from .subject_views import subject_router

views = APIRouter()
views.include_router(assignment_router, prefix="/semester/{semester}/subject/{code}", tags=["assignments"])
views.include_router(exam_router, prefix="/semester/{semester}/subject/{code}", tags=["exams"])
views.include_router(semester_router, prefix="/semester", tags=["semesters"])
views.include_router(subject_router, prefix="/semester/{semester}", tags=["subjects"])


@views.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def home(request: Request, year: Optional[str] = None, session: Session = Depends(get_session)) -> HTMLResponse:
    """Home with optional year filter."""
    query = select(Semester)
    if year:
        query = query.where(Semester.year == year)
    semesters = session.exec(query).all()
    # Distinct years for filter dropdown
    years: List[str] = sorted({s.year for s in session.exec(select(Semester)).all()})
    return _render(request, "index.html", {"semesters": semesters, "years": years, "selected_year": year})


__all__ = ["views"]
