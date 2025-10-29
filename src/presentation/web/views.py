"""HTML view routes rendering Jinja templates (spaces only)."""
from __future__ import annotations

from typing import Optional, List
from datetime import datetime

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
from .types import IndexContext

views = APIRouter()
views.include_router(assignment_router, prefix="/semester/{semester}/subject/{code}", tags=["assignments"])
views.include_router(exam_router, prefix="/semester/{semester}/subject/{code}", tags=["exams"])
views.include_router(semester_router, prefix="/semester", tags=["semesters"])
views.include_router(subject_router, prefix="/semester/{semester}", tags=["subjects"])


@views.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def home(request: Request, year: Optional[str] = None, session: Session = Depends(get_session)) -> HTMLResponse:
    """Home with optional year filter. Defaults to current year when no filter is provided."""
    current_year = str(datetime.now().year)
    has_year_param = "year" in request.query_params

    query = select(Semester)
    if has_year_param:
        # If user supplied year param: filter only when non-empty
        if year:
            query = query.where(Semester.year == year)
        selected_year = year or ""  # empty string denotes 'All'
    else:
        # No explicit filter provided: default to current year
        query = query.where(Semester.year == current_year)
        selected_year = current_year

    semesters = session.exec(query).all()

    # Distinct years for filter dropdown, ensure current year is present
    years_set = {s.year for s in session.exec(select(Semester)).all()}
    years_set.add(current_year)
    years: List[str] = sorted(years_set)

    ctx: IndexContext = {
        "semesters": semesters,
        "years": years,
        "selected_year": selected_year,
        "current_year": current_year,
    }

    return _render(request, "index.html", ctx)


__all__ = ["views"]
