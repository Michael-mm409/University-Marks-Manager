from __future__ import annotations
"""HTML view routes rendering Jinja templates (spaces only)."""
 
from typing import Optional, List, cast
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from sqlmodel import Session, select, col
import re

from src.presentation.api.deps import get_session
from src.infrastructure.db.models import (
    Semester,
    Subject,
    SubjectPrerequisite,
    UserCourse,
    Course,
)
from .template_helpers import _render
from .assignment_views import assignment_router
from .exam_views import exam_router
from .semester_views import semester_router, build_semester_context
from .subject_views import subject_router, build_subject_context, build_subject_page_context
from .course_views import router as course_router
from .settings_views import router as settings_router
from .auth_views import router as auth_router
from .types import IndexContext
from src.core.services.semester_manager import SemesterManager
from src.core.services.course_manager import CourseManager
from src.core.services.grade_calculator import GradeCalculator

from typing import Optional, List, cast
from datetime import datetime

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
from .subject_views import subject_router, build_subject_context, build_subject_page_context
from .course_views import router as course_router
from .settings_views import router as settings_router
from .types import IndexContext
from src.core.services.semester_manager import SemesterManager
from src.core.services.course_manager import CourseManager
from src.core.services.grade_calculator import GradeCalculator

views = APIRouter()
views.include_router(auth_router, prefix="", tags=["auth"])
views.include_router(assignment_router, prefix="/semester/{semester}/subject/{code}", tags=["assignments"])
views.include_router(exam_router, prefix="/semester/{semester}/subject/{code}", tags=["exams"])
views.include_router(semester_router, prefix="/semester", tags=["semesters"])
views.include_router(subject_router, prefix="", tags=["subjects"])
views.include_router(course_router, prefix="", tags=["courses"])
views.include_router(settings_router, prefix="", tags=["settings"])


def _require_user(request: Request) -> Optional[int]:
    """Helper to verify user is logged in and return user_id, or None if not logged in."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return int(user_id)


def _render_home_body(request: Request, session: Session, parsed_year: Optional[int]) -> HTMLResponse:
    """Render Home with a concrete parsed_year (None means All years)."""
    # Verify user is logged in
    user_id = _require_user(request)
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    sm = SemesterManager(session)
    cm = CourseManager(session)
    
    # Get only courses for this user
    user_courses = session.exec(
        select(UserCourse).where(UserCourse.user_id == user_id)
    ).all()
    user_course_ids = [uc.course_id for uc in user_courses]
    
    if not user_course_ids:
        # No courses assigned to user - show helpful message
        ctx: IndexContext = {
            "semesters": [],
            "years": [],
            "selected_year": parsed_year,
            "current_year": str(datetime.now().year),
            "flash_message": "Welcome! You haven't added any courses yet. Visit your profile to add courses.",
            "course_filter": None,
            "wam": None,
            "gpa": None,
            "grade_counts": None,
            "no_courses_warning": True,
            "user_courses": [],
            "username": request.session.get("username"),
        }
        return _render(request, "index.html", ctx)
    
    # Verify and get active course - must be in user's courses
    sess = request.session
    active_course_id = sess.get("current_course_id")
    cid = None
    
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
            # Verify user has access to this course
            if cid not in user_course_ids:
                cid = None
        except Exception:
            cid = None
    
    # If no valid active course, select the default or first available
    if cid is None:
        default_uc = session.exec(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.is_default == True
            )
        ).first()
        
        if default_uc:
            cid = default_uc.course_id
        elif user_course_ids:
            cid = user_course_ids[0]
    
    # Update session with active course info
    if cid is not None:
        course = session.get(Course, cid)
        if course:
            sess["current_course_id"] = cid
            sess["current_course_name"] = course.name
            sess["current_course_code"] = course.code

    if cid is not None:
        all_semesters = sm.get_semesters_for_course(cid)
        years = sm.get_distinct_years_for_course(cid)
    else:
        all_semesters = []
        years = []

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

    # Get user's courses for the course selector in template
    user_courses_data = []
    for uc in user_courses:
        course = session.get(Course, uc.course_id)
        if course:
            user_courses_data.append({
                "id": uc.id,
                "course": course,
                "is_default": uc.is_default,
                "is_active": uc.course_id == cid
            })

    # Calculate grades fresh from database each time (never cached in session)
    gc = GradeCalculator(session)
    wam = gc.calculate_wam(cid)
    gpa = gc.calculate_gpa(cid)
    grade_counts = gc.calculate_grade_counts(cid)

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
        "user_courses": user_courses_data,
        "username": sess.get("username"),
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
    # Check if user is logged in
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)
    
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
    cm = CourseManager(session)
    user_id = int(request.session.get("user_id"))
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
        # Check if any courses exist
        all_courses = cm.get_all_courses()
        if all_courses:
            # Auto-select the first (default) course
            default_course = all_courses[0]
            cid = default_course.id
            sess["current_course_id"] = cid
            sess["current_course_name"] = default_course.name
            sess["current_course_code"] = default_course.code
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


def _infer_level_from_text(text: str) -> Optional[int]:
    """Infer the level (1,2,3,4,...) from the numeric part in subject code.
    
    For undergraduate (first digit 1-5): uses the first digit as level
    For postgraduate (first digit 6+): uses the second digit as level to separate streams
    
    Examples: 
    - CSIT101 -> 101 -> first digit 1 -> level 1
    - CSIT201 -> 201 -> first digit 2 -> level 2
    - MADS6001 -> 6001 -> first digit 6, second digit 0 -> level 0 (or 10)
    - MADS6101 -> 6101 -> first digit 6, second digit 1 -> level 1 (or 11)
    """
    if not text:
        return None
    # Find the first sequence of one or more digits
    m = re.search(r"(\d+)", text)
    if m:
        try:
            digit_sequence = m.group(1)
            first_digit = int(digit_sequence[0])
            
            # For postgraduate (6+), use second digit for finer separation
            if first_digit >= 6:
                if len(digit_sequence) >= 2:
                    second_digit = int(digit_sequence[1])
                    # Return level as 10 + second_digit to keep postgrad separate from undergrad
                    return 10 + second_digit
                else:
                    return 10
            else:
                # For undergraduate, use first digit
                return max(1, first_digit)
        except (ValueError, IndexError):
            pass
    return None


@views.get("/year/{year}/prerequisite_graph/json", response_class=JSONResponse)
def prerequisite_graph_all_subjects(
    year: int,
    request: Request,
    session: Session = Depends(get_session),
) -> JSONResponse:
    """Return prerequisite graph data for all subjects in a given year."""
    sess = request.session
    cm = CourseManager(session)
    active_course_id = sess.get("current_course_id")
    cid = None
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
        except Exception:
            cid = None

    # If no course selected, auto-select the first (default) course
    if cid is None:
        all_courses = cm.get_all_courses()
        if all_courses:
            default_course = all_courses[0]
            cid = default_course.id
            sess["current_course_id"] = cid
            sess["current_course_name"] = default_course.name
            sess["current_course_code"] = default_course.code

    if cid is not None:
        semesters = session.exec(
            select(Semester).where(Semester.year == year, Semester.course_id == cid)
        ).all()
    else:
        semesters = session.exec(select(Semester).where(Semester.year == year)).all()
    
    # FIX: Filter None explicitly so type becomes list[int]
    sem_ids = [s.id for s in semesters if s.id is not None]
    if not sem_ids:
        return JSONResponse({"nodes": [], "edges": []})

    # FIX: Use col() for .in_()
    subjects = session.exec(select(Subject).where(col(Subject.semester_id).in_(sem_ids))).all()
    if not subjects:
        return JSONResponse({"nodes": [], "edges": []})

    by_id = {s.id: s for s in subjects if s.id is not None}
    subject_ids = list(by_id.keys())

    # FIX: Use col() for .in_()
    links = session.exec(
        select(SubjectPrerequisite).where(
            col(SubjectPrerequisite.subject_id).in_(subject_ids)
        )
    ).all()

    edges: list[dict] = []
    # Start with all subjects as nodes (not just those with prerequisites)
    subject_node_ids: set[int] = set(subject_ids)
    
    for link in links:
        # FIX: Check for None before casting to int
        if link.subject_id is None:
            continue
            
        sid = int(link.subject_id)
        
        # Only include subject-to-subject prerequisite relationships
        if link.prerequisite_subject_id is not None:
            try:
                pid = int(link.prerequisite_subject_id)
            except (TypeError, ValueError):
                continue
            subject_node_ids.add(sid)
            subject_node_ids.add(pid)
            edges.append(
                {
                    "from": pid,
                    "to": sid,
                    "type": "corequisite" if link.is_corequisite else "prerequisite",
                }
            )

    nodes: list[dict] = []
    # Ensure we have Subject rows for all subject_node_ids
    missing_ids = subject_node_ids - set(by_id.keys())
    if missing_ids:
        # FIX: cast set to list explicitly for .in_()
        extra = session.exec(select(Subject).where(col(Subject.id).in_(list(missing_ids)))).all()
        for s in extra:
            if s.id is not None:
                by_id[s.id] = s

    # Group nodes by level for positioning
    nodes_by_level = {}
    level_info = {}
    for sid in sorted(subject_node_ids):
        s = by_id.get(sid)
        if not s:
            continue
        code = str(getattr(s, "subject_code", ""))
        level = _infer_level_from_text(code)
        level = level if level is not None else 0
        
        if level not in nodes_by_level:
            nodes_by_level[level] = []
        nodes_by_level[level].append((sid, code))
    
    # Calculate positions based on level
    level_separation = 220
    node_spacing = 260
    
    for level in sorted(nodes_by_level.keys()):
        nodes_at_level = nodes_by_level[level]
        num_nodes = len(nodes_at_level)
        y = level * level_separation
        
        for index, (sid, code) in enumerate(nodes_at_level):
            x = (index - (num_nodes - 1) / 2) * node_spacing
            node: dict = {
                "id": sid,
                "label": code,
                "main": False,
                "corequisite": False,
                "level": level,
                "x": x,
                "y": y,
                "physics": False,
            }
            nodes.append(node)

    return JSONResponse({"nodes": nodes, "edges": edges})

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

@views.get("/all/prerequisite_graph/json", response_class=JSONResponse)
def prerequisite_graph_all_years(
    request: Request,
    session: Session = Depends(get_session),
) -> JSONResponse:
    """Return prerequisite graph data for all subjects in the active course (all years)."""
    sess = request.session
    active_course_id = sess.get("current_course_id")
    cid = None
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
        except Exception:
            cid = None

    if cid is not None:
        semesters = session.exec(
            select(Semester).where(Semester.course_id == cid)
        ).all()
    else:
        semesters = session.exec(select(Semester)).all()

    # FIX: Filter None explicitly
    sem_ids = [s.id for s in semesters if s.id is not None]
    if not sem_ids:
        return JSONResponse({"nodes": [], "edges": []})

    # FIX: Use col()
    subjects = session.exec(select(Subject).where(col(Subject.semester_id).in_(sem_ids))).all()
    if not subjects:
        return JSONResponse({"nodes": [], "edges": []})

    by_id = {s.id: s for s in subjects if s.id is not None}
    subject_ids = list(by_id.keys())

    # FIX: Use col()
    links = session.exec(
        select(SubjectPrerequisite).where(
            col(SubjectPrerequisite.subject_id).in_(subject_ids)
        )
    ).all()

    edges: list[dict] = []
    # Start with all subjects as nodes (not just those with prerequisites)
    subject_node_ids: set[int] = set(subject_ids)
    
    for link in links:
        # FIX: Check for None
        if link.subject_id is None:
            continue
        sid = int(link.subject_id)

        # Only include subject-to-subject prerequisite relationships
        if link.prerequisite_subject_id is not None:
            try:
                pid = int(link.prerequisite_subject_id)
            except (TypeError, ValueError):
                continue
            subject_node_ids.add(sid)
            subject_node_ids.add(pid)
            edges.append(
                {
                    "from": pid,
                    "to": sid,
                    "type": "corequisite" if link.is_corequisite else "prerequisite",
                }
            )

    nodes: list[dict] = []
    missing_ids = subject_node_ids - set(by_id.keys())
    if missing_ids:
        # FIX: use col() and explicit list cast
        extra = session.exec(select(Subject).where(col(Subject.id).in_(list(missing_ids)))).all()
        for s in extra:
            if s.id is not None:
                by_id[s.id] = s

    # Group nodes by level for positioning
    nodes_by_level = {}
    for sid in sorted(subject_node_ids):
        s = by_id.get(sid)
        if not s:
            continue
        code = str(getattr(s, "subject_code", ""))
        level = _infer_level_from_text(code)
        level = level if level is not None else 0
        
        if level not in nodes_by_level:
            nodes_by_level[level] = []
        nodes_by_level[level].append((sid, code))
    
    # Calculate positions based on level
    level_separation = 220
    node_spacing = 260
    
    nodes: list[dict] = []
    for level in sorted(nodes_by_level.keys()):
        nodes_at_level = nodes_by_level[level]
        num_nodes = len(nodes_at_level)
        y = level * level_separation
        
        for index, (sid, code) in enumerate(nodes_at_level):
            x = (index - (num_nodes - 1) / 2) * node_spacing
            node: dict = {
                "id": sid,
                "label": code,
                "main": False,
                "corequisite": False,
                "level": level,
                "x": x,
                "y": y,
                "physics": False,
            }
            nodes.append(node)

    return JSONResponse({"nodes": nodes, "edges": edges})

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


@views.head("/year/{year}/semester/{semester}/subject/{code}", response_class=HTMLResponse)
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
        - Calls build_subject_page_context(session, semester, year, code, exam_weight=..., final_total=..., total_mark=..., return_to=...)
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
        ctx = build_subject_page_context(
            session=session,
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
) -> Response:
    """Shorter subject URL. Standard joins used to satisfy Pylance and prevent Cartesian products."""
    qp = request.query_params
    offering = qp.get("offering")
    return_to = qp.get("return_to") or request.session.pop("return_to", None)

    if semester:
        # Redirect to canonical route
        return RedirectResponse(url=f"/year/{year}/semester/{semester}/{code}", status_code=303)

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
                ctx = build_subject_page_context(session, semester=sem_obj.name, year=year, code=code, return_to=return_to)
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
                        ctx = build_subject_page_context(session, semester=sem_obj.name, year=year, code=code, return_to=return_to)
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
        
        ctx = build_subject_page_context(
            session=session,
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
        sem_obj = session.get(Semester, s.semester_id)
        sem_name = sem_obj.name if sem_obj else "Unknown"
        links.append(f"<li><a href='/year/{year}/semester/{sem_name}/subject/{code}'>Semester {sem_name}</a></li>")
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
    return RedirectResponse(url=f"/year/{year}/semester/{semester}/subject/{code}", status_code=303)


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
