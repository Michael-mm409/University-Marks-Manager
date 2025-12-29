"""HTML view routes rendering Jinja templates (spaces only)."""
from __future__ import annotations

from typing import Optional, List, cast
from datetime import datetime
from urllib import request

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session, select

from src.presentation.api.deps import get_session
from src.infrastructure.db.models import (
    Semester,
    Subject,
)
from .template_helpers import _render
from .assignment_views import assignment_router
from .exam_views import exam_router
from .semester_views import semester_router, build_semester_context
from .subject_views import subject_router, build_subject_context
from .course_views import router as course_router
from .settings_views import router as settings_router
from .types import IndexContext
from src.core.services.semester_manager import SemesterManager
from src.core.services.course_manager import CourseManager
from src.core.services.grade_calculator import GradeCalculator

views = APIRouter()
views.include_router(assignment_router, prefix="/semester/{semester}/subject/{code}", tags=["assignments"])
views.include_router(exam_router, prefix="/semester/{semester}/subject/{code}", tags=["exams"])
views.include_router(semester_router, prefix="/semester", tags=["semesters"])
views.include_router(subject_router, prefix="/semester/{semester}", tags=["subjects"])
views.include_router(course_router, prefix="", tags=["courses"])
views.include_router(settings_router, prefix="", tags=["settings"])


def _render_home_body(request: Request, session: Session, parsed_year: Optional[int]) -> HTMLResponse:
    """Render Home with a concrete parsed_year (None means All years)."""
    sm = SemesterManager(session)
    cm = CourseManager(session)
    
    # Check if any courses exist - show warning if empty
    all_courses = cm.get_all_courses()
    if not all_courses:
        # No courses exist - show a message prompting course creation
        ctx: IndexContext = {
            "semesters": [],
            "years": [],
            "selected_year": parsed_year,
            "current_year": str(datetime.now().year),
            "flash_message": None,
            "course_filter": None,
            "wam": None,
            "gpa": None,
            "grade_counts": None,
            "no_courses_warning": True,
        }
        return _render(request, "index.html", ctx)
    
    # If a course is selected, restrict semesters and years to that course
    # Resolve active course id robustly (fallback to code lookup)
    sess = request.session
    # Debug: log the current session active course keys to help trace state
    try:
        print(f"[debug] _render_home_body session current_course_id={sess.get('current_course_id')!r} current_course_name={sess.get('current_course_name')!r} current_course_code={sess.get('current_course_code')!r}")
    except Exception:
        pass
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

    # If the selected year is not in the available years for this course, fallback to All
    if parsed_year is not None and parsed_year not in years:
        parsed_year = None

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

    # Calculate WAM
    gc = GradeCalculator(session)
    wam = gc.calculate_wam(cid)
    gpa = gc.calculate_gpa(cid)
    grade_counts = gc.calculate_grade_counts(cid)
    print(f"[debug] Passing to template: gpa={gpa}, wam={wam}, course_id={cid}")
    # ...existing code...

    ctx: IndexContext = {
        "semesters": display_semesters,
        "years": years,
        "selected_year": parsed_year,
        "current_year": str(datetime.now().year),
        "flash_message": flash_message,
        "course_filter": course_filter,
        "wam": wam,
        "gpa": gpa,
        "grade_counts": grade_counts,
        "no_courses_warning": False,
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
    # Determine if a course is selected
    sess = request.session
    active_course_id = sess.get("current_course_id")
    cid = None
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
        except Exception:
            cid = None
    if cid is not None:
        years = sm.get_distinct_years_for_course(cid)
        semesters = sm.get_semesters_for_course(cid)
    else:
        years = sm.get_distinct_years()
        semesters = sm.get_all_semesters()
    now_year = int(datetime.now().year)
    # Only redirect to current year if there are semesters for that year
    if now_year in years and any(int(s.year) == now_year for s in semesters):
        return cast(HTMLResponse, RedirectResponse(url=f"/year/{now_year}{selected_suffix}", status_code=303))
    elif years:
        first_year = min(years)
        return cast(HTMLResponse, RedirectResponse(url=f"/year/{first_year}{selected_suffix}", status_code=303))
    return _render_home_body(request, session, None)


@views.get("/year/{year}", response_class=HTMLResponse)
def home_year(request: Request, year: int, session: Session = Depends(get_session)) -> HTMLResponse:
    """
    Short description.

    Args:
        request: Description.
        year: Description.
        session: Description.

    Returns:
        Description.

    Raises:
        Description.
    """
    return _render_home_body(request, session, year)


@views.head("/year/{year}")
def home_year_head(request: Request, year: int, session: Session = Depends(get_session)):
    """HEAD variant for year overview: return same status/headers as GET but no body.

    This reuses the GET view to compute the same headers so HEAD checks succeed.
    """
    resp = home_year(request=request, year=year, session=session)
    headers = dict(resp.headers) if resp is not None else {}
    return Response(status_code=resp.status_code if resp is not None else 200, headers=headers)


@views.get("/all", response_class=HTMLResponse)
def home_all(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    """Render the All years page, or redirect to current/first year if appropriate."""
    sm = SemesterManager(session)
    sess = request.session
    active_course_id = sess.get("current_course_id")
    cid = None
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
        except Exception:
            cid = None
    if cid is not None:
        years = sm.get_distinct_years_for_course(cid)
        semesters = sm.get_semesters_for_course(cid)
    else:
        years = sm.get_distinct_years()
        semesters = sm.get_all_semesters()
    now_year = int(datetime.now().year)
    selected_suffix = "?selected=1" if request.query_params.get("selected") == "1" else ""
    # Only redirect if this is a legacy redirect (e.g., has ?redirect=1)
    if request.query_params.get("redirect") == "1":
        if now_year in years and any(int(s.year) == now_year for s in semesters):
            return cast(HTMLResponse, RedirectResponse(url=f"/year/{now_year}{selected_suffix}", status_code=303))
        elif years:
            first_year = min(years)
            return cast(HTMLResponse, RedirectResponse(url=f"/year/{first_year}{selected_suffix}", status_code=303))
    # Otherwise, render all years view (even if empty)
    return _render_home_body(request, session, None)


@views.get("/year/{year}/semester/{semester}", response_class=HTMLResponse)
def semester_detail_pretty(
    request: Request,
    year: int,
    semester: str,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    """Render the semester overview page for a given year and semester.

    This pretty URL replaces legacy redirects and returns a rendered
    `semester.html` with subject summaries for the selected term.
    """
    ctx = build_semester_context(session, semester=semester, year=str(year))
    # If there are no subjects/semester, still render the page with empty lists
    # build_semester_context always returns a context dict
    return _render(request, "semester.html", ctx)


@views.get("/year/{year}/semester/{semester}/subject/{code}", response_class=HTMLResponse)
def subject_detail_pretty(
        request: Request,
        year: str,
        semester: str,
        code: str,
        session: Session = Depends(get_session),
) -> HTMLResponse:
        """
        Render a subject detail HTML page with optional projected-mark query parameters.

        This view reads optional query parameters from the incoming request to support
        on-the-fly projections and then builds a rendering context for the subject page.

        Behavior:
        - Reads the following optional query parameters from request.query_params:
                - "exam_weight": parsed to float when present and non-empty; invalid values
                    are ignored and cause a one-time flash message to be written to the session
                    (if possible).
                - "final_total": forwarded as-is (string) to the context builder.
                - "total_mark": forwarded as-is (string) to the context builder.
                - "return_to": forwarded as-is to the context builder.
        - If "exam_weight" is missing or empty, it is treated as None.
        - Any ValueError during float parsing of exam_weight is caught; parsed_exam_weight
            becomes None and an attempt is made to set request.session["flash_message"]
            with an explanatory message. Errors while writing the flash message are ignored.
        - Calls build_subject_context(session, semester, year, code, exam_weight=..., final_total=..., total_mark=..., return_to=...)
            to construct the context used to render the page.
        - If the context builder returns None, the view returns an HTMLResponse with
            a 404 status ("Subject not found").
        - Otherwise the view renders and returns the "subject.html" template using _render.

        Parameters:
        - request (Request): the incoming HTTP request (used for query params and session).
        - year (str): academic year identifier for the subject lookup.
        - semester (str): semester identifier for the subject lookup.
        - code (str): subject/code identifier for the subject lookup.
        - session (Session): database/session dependency (defaults to Depends(get_session)).

        Returns:
        - HTMLResponse: either the rendered subject page (200) or a 404 response when the
            subject is not found.

        Side effects:
        - May set request.session["flash_message"] once when an invalid exam_weight is supplied.
        - Uses dependency injection to acquire a session (get_session).

        Notes:
        - final_total and total_mark are forwarded as provided (no parsing/validation).
        - exam_weight accepts numeric input and is resilient to invalid formats.
        """
        # Support optional query params for projections
        qp = request.query_params
        exam_weight = qp.get("exam_weight")
        final_total = qp.get("final_total")
        total_mark = qp.get("total_mark")
        # Defensive parse for exam_weight
        parsed_exam_weight: Optional[float] = None
        if exam_weight not in (None, ""):
                try:
                        parsed_exam_weight = float(exam_weight)  # type: ignore[arg-type]
                except ValueError:
                        parsed_exam_weight = None
                        # Optional: set a one-time message (shown on pages that render flash_message)
                        try:
                                request.session["flash_message"] = "Ignored invalid exam_weight query parameter."
                        except Exception:
                                pass
        ctx = build_subject_context(
                session,
                semester=semester,
                year=year,
                code=code,
                exam_weight=parsed_exam_weight,
                final_total=final_total,
                total_mark=total_mark,
            return_to=qp.get("return_to"),
            error_message=qp.get("error"),
        )
        if ctx is None:
                return HTMLResponse("Subject not found", status_code=404)
        return _render(request, "subject.html", ctx)

@views.get("/subjects/{year}/{code}", response_class=HTMLResponse)
def subject_detail_short(
    request: Request,
    year: str,
    code: str,
    semester: Optional[str] = None,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    """Shorter subject URL. Standard joins used to satisfy Pylance and prevent Cartesian products."""
    qp = request.query_params
    offering = qp.get("offering")
    return_to = qp.get("return_to") or request.session.pop("return_to", None)

    if semester:
        ctx = build_subject_context(
            session,
            semester=semester,
            year=year,
            code=code,
            return_to=return_to,
            error_message=qp.get("error"),
        )
        if ctx is None:
            return HTMLResponse("Subject not found", status_code=404)
        return _render(request, "subject.html", ctx)

    if offering:
        # Join using the Relationship attribute 'Subject.semester'
        # This is the cleanest way to avoid the "bool" type error
        candidate = session.exec(
            select(Subject)
            .join(Semester) 
            .where(
                Semester.year == year,
                Subject.subject_code == code,
                Semester.name == offering
            )
        ).all()
        if len(candidate) == 1:
            subj = candidate[0]
            sem_obj = session.get(Semester, subj.semester_id)
            if sem_obj:
                ctx = build_subject_context(session, semester=sem_obj.name, year=year, code=code, return_to=return_to)
                if ctx:
                    return _render(request, "subject.html", ctx)

        parts = [p for p in offering.split("-") if p]
        if parts:
            for token in parts:
                candidate = session.exec(
                    select(Subject)
                    .join(Semester)
                    .where(
                        Semester.year == year,
                        Subject.subject_code == code,
                        Semester.name == token
                    )
                ).all()
                if len(candidate) == 1:
                    subj = candidate[0]
                    sem_obj = session.get(Semester, subj.semester_id)
                    if sem_obj:
                        ctx = build_subject_context(session, semester=sem_obj.name, year=year, code=code, return_to=return_to)
                        if ctx:
                            return _render(request, "subject.html", ctx)

    # Final query also updated to use standard join
    rows = session.exec(
        select(Subject)
        .join(Semester)
        .where(
            Semester.year == year,
            Subject.subject_code == code
        )
    ).all()

    if not rows:
        return HTMLResponse("Subject not found", status_code=404)
    
    if len(rows) == 1:
        subj = rows[0]
        sem_obj = session.get(Semester, subj.semester_id)
        if not sem_obj:
            return HTMLResponse("Subject not found", status_code=404)
        
        ctx = build_subject_context(
            session,
            semester=sem_obj.name,
            year=year,
            code=code,
            return_to=return_to,
        )
        if ctx is None:
            return HTMLResponse("Subject not found", status_code=404)
        return _render(request, "subject.html", ctx)

    links = []
    for s in rows:
        # Resolve semester name from related object since it's safer
        sem_obj = session.get(Semester, s.semester_id)
        sem_name = sem_obj.name if sem_obj else "Unknown"
        links.append(f"<li><a href='/subjects/{year}/{code}?semester={sem_name}'>Semester {sem_name}</a></li>")
    
    body = f"<h1>Multiple semesters</h1><p>Choose semester for {code} {year}:</p><ul>{''.join(links)}</ul>"
    return HTMLResponse(body)

@views.post("/subjects/{year}/{code}/open")
def subject_open(
    request: Request,
    year: str,
    code: str,
    semester: str = Form(...),
    return_to: Optional[str] = Form(None),
) -> RedirectResponse:
    """Accept a POST that sets a one-time return_to in session and redirects to the canonical subject GET.

    This prevents the return_to token from appearing in the query string while preserving
    the ability for the subject template to render a 'Back to Semester' link.
    """
    if return_to:
        try:
            request.session["return_to"] = return_to
        except Exception:
            pass
    return RedirectResponse(url=f"/subjects/{year}/{code}?semester={semester}", status_code=303)


@views.head("/year/{year}/semester/{semester}")
def semester_detail_head(
    request: Request,
    year: int,
    semester: str,
    session: Session = Depends(get_session),
):
    """HEAD variant for semester detail: return same status/headers as GET but no body.

    This delegates to the GET handler and returns headers (no body) so HEAD checks succeed
    and remain in sync with what a GET would return.
    """
    # Reuse the GET view to compute the same response/headers
    resp = semester_detail_pretty(request=request, year=year, semester=semester, session=session)
    headers = dict(resp.headers) if resp is not None else {}
    return Response(status_code=resp.status_code if resp is not None else 200, headers=headers)


__all__ = ["views"]
