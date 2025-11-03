"""HTML view routes rendering Jinja templates (spaces only)."""
from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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
from .course_views import router as course_router
from .types import IndexContext
from src.core.services.semester_manager import SemesterManager
from src.core.services.course_manager import CourseManager

views = APIRouter()
views.include_router(assignment_router, prefix="/semester/{semester}/subject/{code}", tags=["assignments"])
views.include_router(exam_router, prefix="/semester/{semester}/subject/{code}", tags=["exams"])
views.include_router(semester_router, prefix="/semester", tags=["semesters"])
views.include_router(subject_router, prefix="/semester/{semester}", tags=["subjects"])
views.include_router(course_router, prefix="", tags=["courses"])


@views.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def home(request: Request, year: Optional[int] = None, session: Session = Depends(get_session)) -> HTMLResponse:
    """Render the semester selection screen with optional year filter.

    This restores the previous behavior: choose a semester (filtered by year),
    while the active course banner appears at the top if a course is selected.
    """
    sm = SemesterManager(session)
    cm = CourseManager(session)
    # If a course is selected, restrict semesters and years to that course
    # Resolve active course id robustly (fallback to code lookup)
    sess = request.session
    active_course_id = sess.get("current_course_id")
    cid = None
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
        except Exception:
            cid = None
    if cid is None:
        code = sess.get("current_course_code")
        if code:
            course = cm.get_course_by_code(str(code))
            course_id = getattr(course, "id", None)
            if course_id is not None:
                cid = int(course_id)
                # Heal the session for future requests
                sess["current_course_id"] = cid
                if course and not sess.get("current_course_name"):
                    sess["current_course_name"] = getattr(course, "name", None)

    if cid is not None:
        all_semesters = sm.get_semesters_for_course(cid)
        years = sm.get_distinct_years_for_course(cid)
    else:
        all_semesters = sm.get_all_semesters()
        years = sm.get_distinct_years()

    display_semesters = [s for s in all_semesters if (year is None or int(s.year) == int(year))]
    # Pop any one-time flash message (set after selecting a course)
    flash_message = request.session.pop("flash_message", None)
    # Fallback: if URL indicates a selection just happened, synthesize a message
    if (flash_message is None) and (request.query_params.get("selected") == "1"):
        cname = request.session.get("current_course_name")
        ccode = request.session.get("current_course_code")
        if cname or ccode:
            if cname and ccode:
                flash_message = f"Active course set to {cname} ({ccode})."
            else:
                flash_message = f"Active course set."

    # Helpful context for template to show filter banner
    course_filter = None
    if cid is not None:
        course_filter = {
            "name": sess.get("current_course_name"),
            "code": sess.get("current_course_code"),
        }

    ctx: IndexContext = {
        "semesters": display_semesters,
        "years": years,
        "selected_year": year,
        "current_year": str(datetime.now().year),
        "flash_message": flash_message,
        "course_filter": course_filter,
    }
    return _render(request, "index.html", ctx)


__all__ = ["views"]
