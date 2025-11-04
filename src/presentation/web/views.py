"""HTML view routes rendering Jinja templates (spaces only)."""
from __future__ import annotations

from typing import Optional, List, cast
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
from .semester_views import semester_router, build_semester_context
from .subject_views import subject_router, build_subject_context
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


def _render_home_body(request: Request, session: Session, parsed_year: Optional[int]) -> HTMLResponse:
    """Render Home with a concrete parsed_year (None means All years)."""
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

    display_semesters = [s for s in all_semesters if (parsed_year is None or int(s.year) == int(parsed_year))]
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
        "selected_year": parsed_year,
        "current_year": str(datetime.now().year),
        "flash_message": flash_message,
        "course_filter": course_filter,
    }
    return _render(request, "index.html", ctx)


@views.api_route("/", methods=["GET"], response_class=HTMLResponse)
def home(request: Request, year: Optional[str] = None, session: Session = Depends(get_session)) -> HTMLResponse:
    """Landing route that supports legacy query param and redirects to pretty URLs.

    - /?year=2025 -> 303 /year/2025 (preserving selected=1)
    - /?year= or /?year=all -> 303 /all (preserving selected=1)
    - / with no year -> if current year exists -> 303 /year/<current>, else render All
    """
    qp = request.query_params
    selected_suffix = "?selected=1" if qp.get("selected") == "1" else ""
    if "year" in qp:
        y = (qp.get("year") or "").strip()
        if y == "" or y.lower() == "all":
            return cast(HTMLResponse, RedirectResponse(url=f"/all{selected_suffix}", status_code=303))
        if y.isdigit():
            return cast(HTMLResponse, RedirectResponse(url=f"/year/{int(y)}{selected_suffix}", status_code=303))
        # invalid -> treat as All
        return cast(HTMLResponse, RedirectResponse(url=f"/all{selected_suffix}", status_code=303))

    # No year provided: prefer current year if any data exists, else All
    sm = SemesterManager(session)
    years = sm.get_distinct_years()
    now_year = int(datetime.now().year)
    if now_year in years:
        return cast(HTMLResponse, RedirectResponse(url=f"/year/{now_year}{selected_suffix}", status_code=303))
    return _render_home_body(request, session, None)


@views.get("/year/{year}", response_class=HTMLResponse)
def home_year(request: Request, year: int, session: Session = Depends(get_session)) -> HTMLResponse:
    return _render_home_body(request, session, year)


@views.get("/all", response_class=HTMLResponse)
def home_all(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    return _render_home_body(request, session, None)


@views.get("/year/{year}/semester/{semester}", response_class=HTMLResponse)
def semester_detail_pretty(
    request: Request,
    year: str,
    semester: str,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    ctx = build_semester_context(session, semester=semester, year=year)
    return _render(request, "semester.html", ctx)


@views.get("/year/{year}/semester/{semester}/subject/{code}", response_class=HTMLResponse)
def subject_detail_pretty(
    request: Request,
    year: str,
    semester: str,
    code: str,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    # Support optional query params for projections
    qp = request.query_params
    exam_weight = qp.get("exam_weight")
    final_total = qp.get("final_total")
    total_mark = qp.get("total_mark")
    ctx = build_subject_context(
        session,
        semester=semester,
        year=year,
        code=code,
        exam_weight=float(exam_weight) if (exam_weight not in (None, "")) else None,
        final_total=final_total,
        total_mark=total_mark,
        return_to=qp.get("return_to"),
    )
    if ctx is None:
        return HTMLResponse("Subject not found", status_code=404)
    return _render(request, "subject.html", ctx)


__all__ = ["views"]
