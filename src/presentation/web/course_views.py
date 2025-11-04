"""Web views for managing courses."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlmodel import Session, select

from src.core.services.course_manager import CourseManager
from src.core.services.semester_manager import SemesterManager
from src.infrastructure.db.engine import get_session
from src.infrastructure.db.models import Subject, Course, Semester

router = APIRouter()


def _resolve_course(course_manager: CourseManager, key: str) -> Optional[Course]:
    """Resolve a course by code or numeric id (backward compatible).

    Prefer code lookup FIRST, even if the key is all-digits, to support numeric codes like "000".
    Fallback to numeric id lookup only if code lookup fails and the key is digits.
    """
    # Try by code first (supports numeric codes like "000")
    by_code = course_manager.get_course_by_code(key)
    if by_code:
        return by_code
    # Fallback to id only when code lookup fails
    if key.isdigit():
        return course_manager.get_course_by_id(int(key))
    return None


@router.get("/courses", response_class=HTMLResponse)
def get_courses_page(
    request: Request,
    session: Session = Depends(get_session),
):
    """Render the main page for managing courses."""
    jinja_env = request.app.state.jinja_env
    course_manager = CourseManager(session)
    courses = course_manager.get_all_courses()
    template = jinja_env.get_template("courses.html")
    return template.render(request=request, courses=courses)


@router.get("/courses/_codes", response_class=HTMLResponse)
@router.get("/courses/_debug/codes", response_class=HTMLResponse)
def debug_course_codes(
    request: Request,
    session: Session = Depends(get_session),
):
    """Debug page: list all course codes with raw/trimmed values and potential collisions.

    Useful for spotting trailing spaces or inconsistent casing in Course.code.
    """
    # Gate behind env flag and optional token
    app = request.app
    if not getattr(app.state, "enable_debug_routes", False):
        return HTMLResponse("Not found", status_code=404)
    expected = getattr(app.state, "debug_token", None)
    if expected and request.query_params.get("token") != expected:
        return HTMLResponse("Not found", status_code=404)
    cm = CourseManager(session)
    courses = cm.get_all_courses()
    # Build a simple HTML table (no separate template needed)
    def esc(s: str) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
    rows = []
    for c in courses:
        code = c.code or ""
        trimmed = code.strip()
        rows.append(
            f"<tr>"
            f"<td>{c.id}</td>"
            f"<td>{esc(c.name)}</td>"
            f"<td class='codecell'><code>{esc(repr(code))}</code></td>"
            f"<td style='text-align:right'>{len(code)}</td>"
            f"<td class='codecell'><code>{esc(repr(trimmed))}</code></td>"
            f"<td style='text-align:right'>{len(trimmed)}</td>"
            f"</tr>"
        )
    # Detect potential collisions after TRIM+lower()
    from collections import defaultdict
    buckets = defaultdict(list)
    for c in courses:
        norm = (c.code or "").strip().lower()
        if norm:
            buckets[norm].append(c)
    collisions = {k: v for k, v in buckets.items() if len(v) > 1}

    html = [
        "<html><head><title>Course Codes Debug</title>",
        "<meta name=\"robots\" content=\"noindex,nofollow\">",
        # Tailwind may or may not be present; add inline CSS fallback for readability
        "<link rel=\"stylesheet\" href=\"/static/css/tailwind.css\">",
        "<style>",
        ":root{color-scheme:light dark;}\n",
    "body{margin:16px;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,\"Apple Color Emoji\",\"Segoe UI Emoji\";color:#111;background:#ffffff;}\n",
        ".container{max-width:1200px;margin:0 auto;}\n",
        "table{border-collapse:collapse;width:100%;table-layout:fixed;}\n",
    "thead th{background:#f3f4f6;color:#111;text-align:left;}\n",
        "th,td{border:1px solid #e5e7eb;padding:8px 10px;vertical-align:top;}\n",
        "col.id{width:64px;}col.name{width:320px;}col.code{width:300px;}col.len{width:80px;}col.trim{width:300px;}col.trimlen{width:100px;}\n",
        "code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,\"Liberation Mono\",monospace;font-size:12px;}\n",
        ".codecell{white-space:pre-wrap;word-break:break-word;}\n",
        ".muted{opacity:.75;}\n",
    "@media (prefers-color-scheme: dark){\n",
    "  body{background:#111827;color:#e5e7eb;}\n",
    "  thead th{background:#374151;color:#e5e7eb;}\n",
    "  th,td{border-color:#374151;}\n",
    "}\n",
        "</style>",
        "</head><body>",
        "<div class='container'>",
        "<h1 style='font-size:1.25rem;font-weight:600;margin:0 0 0.5rem;'>Course Codes (raw vs trimmed)</h1>",
        "<p class='muted' style='margin:0 0 1rem;'>This debug page helps identify trailing spaces or case inconsistencies. Raw values are shown using Python repr().</p>",
        "<div style='overflow-x:auto;'>",
        "<table>",
        "<colgroup>",
        "<col class='id'/><col class='name'/><col class='code'/><col class='len'/><col class='trim'/><col class='trimlen'/>",
        "</colgroup>",
        "<thead><tr>",
        "<th>id</th>",
        "<th>name</th>",
        "<th>code (raw)</th>",
        "<th>len</th>",
        "<th>trimmed</th>",
        "<th>trim_len</th>",
        "</tr></thead>",
        "<tbody>",
        *rows,
        "</tbody></table></div>",
        "</div>",
        "</body></html>",
    ]
    if collisions:
        html += [
            "<div class='container' style='margin-top:1rem'>",
            "<h2 style='font-size:1.125rem;font-weight:600'>Potential collisions after TRIM+lower()</h2>",
            "<ul style='margin-top:.5rem;padding-left:1.25rem;list-style:disc'>",
        ]
        for k, vs in collisions.items():
            ids = ", ".join(str(v.id) for v in vs)
            codes = ", ".join(esc(v.code or "") for v in vs)
            html.append(f"<li><code>{esc(k)}</code> -> ids [{ids}], codes [{codes}]</li>")
        html.append("</ul></div>")
    else:
        html.append("<p class='container muted' style='margin-top:1rem'>No collisions detected after TRIM+lower().</p>")
    return HTMLResponse("".join(html))


@router.get("/courses/_resolve/{key}")
def debug_resolve_course(key: str, request: Request, session: Session = Depends(get_session)):
    """Return how a course key resolves (by_code or by_id) and the course info.

    Helpful for debugging why numeric codes like "000" may not resolve in routes.
    """
    app = request.app
    if not getattr(app.state, "enable_debug_routes", False):
        return JSONResponse({"detail": "Not found"}, status_code=404)
    expected = getattr(app.state, "debug_token", None)
    if expected and request.query_params.get("token") != expected:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    cm = CourseManager(session)
    # Try code first
    course = cm.get_course_by_code(key)
    matched_by = "code" if course else None
    if not course and key.isdigit():
        course = cm.get_course_by_id(int(key))
        matched_by = "id" if course else None
    if not course:
        return JSONResponse({"matched_by": None, "found": False}, status_code=404)
    return JSONResponse({
        "matched_by": matched_by,
        "found": True,
        "course": {
            "id": course.id,
            "name": course.name,
            "code": course.code,
        }
    })


@router.post("/courses/", response_class=HTMLResponse)
def create_course_view(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    session: Session = Depends(get_session),
):
    """Handle the form submission to create a new course and return the HTML fragment."""
    jinja_env = request.app.state.jinja_env
    course_manager = CourseManager(session)
    course = course_manager.create_course(name=name, code=code)
    template = jinja_env.get_template("partials/course_item.html")
    return template.render(request=request, course=course)


@router.get("/courses/{course_code}", response_class=HTMLResponse)
def get_course_detail_page(
    request: Request,
    course_code: str,
    session: Session = Depends(get_session),
):
    """Render the detail page for a specific course."""
    jinja_env = request.app.state.jinja_env
    course_manager = CourseManager(session)
    semester_manager = SemesterManager(session)

    course = _resolve_course(course_manager, course_code)
    if not course:
        # Handle course not found, maybe redirect or show an error page
        # For now, we'll just return a simple error
        return HTMLResponse("Course not found", status_code=404)

    # Assigned semesters for this course
    assigned_semesters = list(getattr(course, "semesters", []) or [])
    # Unassigned (available) semesters and years
    unassigned_semesters = course_manager.get_unassigned_semesters()
    unassigned_years = course_manager.get_unassigned_years()

    # Map assigned semester -> subjects within that term for optional display
    subjects_by_semester: dict[int, list[Subject]] = {}
    for sem in assigned_semesters:
        year_col: Any = Subject.year
        candidates = session.exec(
            select(Subject).where(
                Subject.semester_name == sem.name,
                year_col == str(sem.year),
            )
        ).all()
        subjects_by_semester[getattr(sem, "id")] = list(candidates)

    template = jinja_env.get_template("course_detail.html")
    return template.render(
        request=request,
        course=course,
        assigned_semesters=assigned_semesters,
        unassigned_semesters=unassigned_semesters,
        unassigned_years=unassigned_years,
        subjects_by_semester=subjects_by_semester,
    )


# Removed subject-level linking UI per requirements


@router.post("/courses/{course_code}/assign-semester", response_class=HTMLResponse)
def assign_semester_to_course_view(
    request: Request,
    course_code: str,
    semester_key: str = Form(...),
    session: Session = Depends(get_session),
):
    """Handle assigning a semester to a course and reload the page."""
    course_manager = CourseManager(session)
    course = _resolve_course(course_manager, course_code)
    if not course:
        return HTMLResponse("Course not found", status_code=404)
    assert course.id is not None
    try:
        sem_name, sem_year = semester_key.split("|", 1)
        sem_year_int = int(sem_year)
    except Exception:
        return HTMLResponse("Invalid semester selection", status_code=400)
    # Resolve semester by (name, year)
    from sqlmodel import select
    sem = session.exec(select(Semester).where(Semester.name == sem_name, Semester.year == sem_year_int)).first()
    if not sem:
        return HTMLResponse("Semester not found", status_code=404)
    course_manager.assign_semester_to_course(course_id=course.id, semester_id=sem.id)  # type: ignore[arg-type]

    # Redirect to the same page to see the change
    response = HTMLResponse()
    response.headers["HX-Redirect"] = f"/courses/{course_code}"
    return response


@router.post("/courses/{course_code}/assign-year", response_class=HTMLResponse)
def assign_year_to_course_view(
    request: Request,
    course_code: str,
    year: int = Form(...),
    session: Session = Depends(get_session),
):
    """Assign all semesters for a given year to a course and reload the page."""
    course_manager = CourseManager(session)
    course = _resolve_course(course_manager, course_code)
    if not course:
        return HTMLResponse("Course not found", status_code=404)
    assert course.id is not None
    course_manager.assign_year_to_course(course_id=course.id, year=year)

    response = HTMLResponse()
    response.headers["HX-Redirect"] = f"/courses/{course_code}"
    return response


@router.post("/courses/{course_code}/select")
def select_current_course(
    request: Request,
    course_code: str,
    session: Session = Depends(get_session),
):
    """Persist the selected course in the session and redirect to Home reliably.

    Always returns a 303 to "/" and also sets HX-Redirect for HTMX safety.
    """
    # Minimal session payload; name can be looked up lazily if needed
    sess = request.session
    # Resolve basic course info for display in header (supports code or legacy id)
    course = _resolve_course(CourseManager(session), course_code)
    if course:
        sess["current_course_id"] = course.id
        sess["current_course_name"] = course.name
        if getattr(course, "code", None):
            sess["current_course_code"] = course.code
        else:
            sess.pop("current_course_code", None)
        # one-time flash message for the next page view
        sess["flash_message"] = f"Active course changed to {course.name}{' (' + course.code + ')' if getattr(course, 'code', None) else ''}."
    # If HTMX requested, return an inline success alert instead of redirect
    if request.headers.get("HX-Request"):
        # For HTMX, instruct the browser to navigate to Home (which will default to current year)
        redirect_url = "/?selected=1"
        resp = HTMLResponse("")
        resp.headers["HX-Redirect"] = redirect_url
        return resp

    # Otherwise, return a redirect response to home with a hint for UI to show alert
    redirect_url = "/?selected=1"
    response = RedirectResponse(url=redirect_url, status_code=303)
    response.headers["HX-Redirect"] = redirect_url
    return response


@router.post("/courses/clear-selection")
def clear_current_course(
    request: Request,
):
    """Clear the selected course from the session and redirect to courses list."""
    sess = request.session
    sess.pop("current_course_id", None)
    response = RedirectResponse(url="/courses", status_code=303)
    response.headers["HX-Redirect"] = "/courses"
    return response


@router.post("/courses/{course_code}/assign-all", response_class=HTMLResponse)
def assign_all_semesters_to_course_view(
    request: Request,
    course_code: str,
    session: Session = Depends(get_session),
):
    """Assign all unassigned semesters to a course and reload the page."""
    course_manager = CourseManager(session)
    course = _resolve_course(course_manager, course_code)
    if not course:
        return HTMLResponse("Course not found", status_code=404)
    assert course.id is not None
    course_manager.assign_all_semesters_to_course(course_id=course.id)

    response = HTMLResponse()
    response.headers["HX-Redirect"] = f"/courses/{course_code}"
    return response


@router.post("/courses/{course_code}/unassign-semester", response_class=HTMLResponse)
def unassign_semester_from_course_view(
    request: Request,
    course_code: str,
    semester_name: str = Form(...),
    year: int = Form(...),
    session: Session = Depends(get_session),
):
    """Remove a semester from the course."""
    course_manager = CourseManager(session)
    course = _resolve_course(course_manager, course_code)
    if not course:
        return HTMLResponse("Course not found", status_code=404)
    from sqlmodel import select
    sem = session.exec(select(Semester).where(Semester.name == semester_name, Semester.year == year)).first()
    if not sem:
        return HTMLResponse("Semester not found", status_code=404)
    course_manager.unassign_semester_from_course(course_id=course.id, semester_id=sem.id)  # type: ignore[arg-type]
    if request.headers.get("HX-Request"):
        response = HTMLResponse()
        response.headers["HX-Redirect"] = f"/courses/{course_code}"
        return response
    return RedirectResponse(url=f"/courses/{course_code}", status_code=303)


@router.post("/courses/{course_code}/unassign-year", response_class=HTMLResponse)
def unassign_year_from_course_view(
    request: Request,
    course_code: str,
    year: int = Form(...),
    session: Session = Depends(get_session),
):
    """Remove all semesters for the given year from the course."""
    course_manager = CourseManager(session)
    course = _resolve_course(course_manager, course_code)
    if not course:
        return HTMLResponse("Course not found", status_code=404)
    assert course.id is not None
    course_manager.unassign_year_from_course(course_id=course.id, year=year)
    if request.headers.get("HX-Request"):
        response = HTMLResponse()
        response.headers["HX-Redirect"] = f"/courses/{course_code}"
        return response
    return RedirectResponse(url=f"/courses/{course_code}", status_code=303)

@router.post("/courses/{course_code}/update", response_class=HTMLResponse)
def update_course_view(
    request: Request,
    course_code: str,
    name: str = Form(...),
    code: str = Form(...),
    session: Session = Depends(get_session),
):
    """Update course name and code and redirect to the (possibly new) code path."""
    cm = CourseManager(session)
    course = _resolve_course(cm, course_code)
    if not course:
        return HTMLResponse("Course not found", status_code=404)
    try:
        updated = cm.update_course(course.id, name=name, code=code)  # type: ignore[arg-type]
    except Exception as ex:
        # Likely a uniqueness violation; show simple message
        return HTMLResponse(f"Update failed: {ex}", status_code=400)
    # Update session banner if this course is active
    sess = request.session
    if updated and sess.get("current_course_id") == getattr(updated, "id", None):
        sess["current_course_name"] = getattr(updated, "name", None)
        sess["current_course_code"] = getattr(updated, "code", None)
        sess["flash_message"] = "Course details updated."
    target = f"/courses/{(getattr(updated, 'code', None) or getattr(updated, 'id', ''))}"
    if request.headers.get("HX-Request"):
        resp = HTMLResponse()
        resp.headers["HX-Redirect"] = target
        return resp
    return RedirectResponse(url=target, status_code=303)


@router.post("/courses/{course_code}/delete", response_class=HTMLResponse)
def delete_course_view(
    request: Request,
    course_code: str,
    session: Session = Depends(get_session),
):
    """Delete a course and redirect to courses list; clears active banner if needed."""
    cm = CourseManager(session)
    course = _resolve_course(cm, course_code)
    if not course:
        return HTMLResponse("Course not found", status_code=404)
    cm.delete_course(course.id)  # type: ignore[arg-type]
    # Clear session if active
    sess = request.session
    if sess.get("current_course_id") == course.id:
        sess.pop("current_course_id", None)
        sess.pop("current_course_name", None)
        sess.pop("current_course_code", None)
        sess["flash_message"] = "Course deleted."
    target = "/courses"
    if request.headers.get("HX-Request"):
        resp = HTMLResponse()
        resp.headers["HX-Redirect"] = target
        return resp
    return RedirectResponse(url=target, status_code=303)
