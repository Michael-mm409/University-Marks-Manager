from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select, col
from typing import List, Optional
from sqlalchemy.sql import expression
from fastapi.templating import Jinja2Templates

from src.presentation.api.deps import get_session
from src.infrastructure.db.models import Subject, Assignment, Examination, ExamSettings, GradeType, Semester, SubjectPrerequisite
from src.presentation.web.utils.subject_helpers import (
    resolve_subject_for_context,
    build_candidate_subjects,
)
from .utils.graph_helpers import build_subject_prerequisite_graph
from .utils.marks_helpers import compute_subject_marks_summary
from .utils.subject_commands import (
    create_subject_core,
    add_prerequisite_core,
)
from .utils.subject_context import build_subject_context as build_subject_context_core
from .types import SubjectContext

subject_router = APIRouter()


def extract_semester_order(semester_name: str) -> int:
    """
    Extract the chronological order of a semester from its name.
    
    Supports:
    - Named semesters: Annual (0), Autumn/Fall (1), Spring (2), Summer (3), Winter (4)
    - Numbered semesters: Trimester 1/T1 (1), Trimester 2/T2 (2), etc.
    - Quarters: Quarter 1/Q1 (1), Quarter 2/Q2 (2), etc.
    
    Returns:
        An integer representing the semester's position within a year.
        Higher numbers = later in the year. 0 = full year/annual course.
    """
    import re
    
    name_lower = semester_name.lower().strip()
    
    # Check for annual/full-year courses first (they have their own order: 0)
    if "annual" in name_lower or "full year" in name_lower or "full-year" in name_lower:
        return 0
    
    # Try to extract a number from the semester name (e.g., "Trimester 1" -> 1, "T3" -> 3, "Q2" -> 2)
    number_match = re.search(r'(\d+)', name_lower)
    if number_match:
        extracted_num = int(number_match.group(1))
        # Validate that the number is reasonable (1-4 for most systems)
        if 1 <= extracted_num <= 4:
            return extracted_num
    
    # Named semester mapping (fallback for traditional semester names)
    named_semesters = {
        "autumn": 1,
        "fall": 1,
        "spring": 2,
        "summer": 3,
        "winter": 4,
    }
    
    return named_semesters.get(name_lower, 999)  # 999 for unknown semesters


def check_prerequisite_violations(
    session: Session,
    subject: Subject,
    target_semester_name: str,
    target_year: int,
) -> Optional[str]:
    """
    Check if moving a subject to a different semester violates prerequisite constraints.
    
    Returns:
        None if no violations, otherwise a string describing the violation.
    """
    # Get all prerequisites for this subject
    prerequisites = session.exec(
        select(SubjectPrerequisite).where(
            SubjectPrerequisite.subject_id == subject.id
        )
    ).all()
    
    if not prerequisites:
        return None
    
    # Get the target semester object
    target_semester = session.exec(
        select(Semester).where(
            Semester.name == target_semester_name,
            Semester.year == target_year
        )
    ).first()
    
    if not target_semester:
        return None
    
    violations = []
    target_sem_order = extract_semester_order(target_semester_name)
    
    for prereq in prerequisites:
        # Skip custom text prerequisites (they don't have subject_id)
        if not prereq.prerequisite_subject_id:
            continue
        
        prereq_subject = session.get(Subject, prereq.prerequisite_subject_id)
        if not prereq_subject:
            continue
        
        prereq_semester = session.get(Semester, prereq_subject.semester_id)
        if not prereq_semester:
            continue
        
        prereq_sem_order = extract_semester_order(prereq_semester.name)
        
        # If prerequisite is in a later year, that's a violation
        if prereq_semester.year > target_year:
            violations.append(f"{prereq_subject.subject_code}")
        # If same year, check semester order
        elif prereq_semester.year == target_year and prereq_sem_order > target_sem_order:
            violations.append(f"{prereq_subject.subject_code}")
    
    if violations:
        prereq_type = "corequisite" if prerequisites[0].is_corequisite else "prerequisite"
        return f"WARNING: Moving to {target_semester_name} {target_year} would place this subject BEFORE its {prereq_type}(s): {', '.join(violations)}"
    
    return None

templates = Jinja2Templates(directory="src/templates")


def build_subject_context(
    session: Session,
    semester: str,
    year: str,
    code: str,
    exam_weight: Optional[float] = None,
    final_total: Optional[str] = None,
    total_mark: Optional[str] = None,
    return_to: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Optional[SubjectContext]:
    """Thin wrapper around the utility implementation.

    The heavy lifting lives in presentation.web.utils.subject_context.
    This wrapper exists to preserve the public API
    (other modules import build_subject_context from this file).
    """

    return build_subject_context_core(
        session=session,
        semester=semester,
        year=year,
        code=code,
        exam_weight=exam_weight,
        final_total=final_total,
        total_mark=total_mark,
        return_to=return_to,
        error_message=error_message,
    )


def build_subject_page_context(
    session: Session,
    semester: str,
    year: str,
    code: str,
    exam_weight: Optional[float] = None,
    final_total: Optional[str] = None,
    total_mark: Optional[str] = None,
    return_to: Optional[str] = None,
    error_message: Optional[str] = None,
):
    """Build full subject page context including prerequisite candidates."""
    ctx = build_subject_context(
        session=session,
        semester=semester,
        year=year,
        code=code,
        exam_weight=exam_weight,
        final_total=final_total,
        total_mark=total_mark,
        return_to=return_to,
        error_message=error_message,
    )
    if ctx is None:
        return None

    subject = ctx.get("subject")  # type: ignore[index]
    candidate_subjects: List[Subject] = build_candidate_subjects(session, subject)

    page_ctx = dict(ctx)
    page_ctx["candidate_subjects"] = candidate_subjects
    return page_ctx

@subject_router.get(
    "/semester/{semester}/subject/{code}/prerequisite_graph/json",
    response_class=JSONResponse,
)
def prerequisite_graph_for_subject(
    semester: str,
    code: str,
    year: str,
    session: Session = Depends(get_session),
):
    """Return prerequisite graph data for a single subject."""
    try:
        year_int = int(str(year))
    except Exception:
        return JSONResponse({"nodes": [], "edges": []})

    # Resolve the concrete subject using normalized Semester/Subject schema
    subj = session.exec(
        select(Subject)
        .join(Semester)
        .where(
            Semester.name == semester,
            Semester.year == year_int,
            Subject.subject_code == code,
        )
    ).first()
    
    # FIX: Check subj.id explicitly
    if not subj or subj.id is None:
        return JSONResponse({"nodes": [], "edges": []})

    graph = build_subject_prerequisite_graph(session, int(subj.id))
    return JSONResponse(graph)

@subject_router.api_route("/semester/{semester}/subject/create", methods=["POST"])
def create_subject(
    semester: str,
    year: str = Form(...),
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    credit_points: int = Form(6),
    has_exam: Optional[bool] = Form(False),
    sync_subject: Optional[bool] = Form(False),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Create a new subject in the semester if it does not already exist."""
    success = create_subject_core(
        session=session,
        semester=semester,
        year=year,
        subject_code=subject_code,
        subject_name=subject_name,
        credit_points=credit_points,
        has_exam=bool(has_exam),
        sync_subject=bool(sync_subject),
    )

    if not success:
        # Semester not found, redirect with error
        return RedirectResponse(f"/year/{year}/semester/{semester}?error=Semester+not+found", status_code=303)

    # Redirect back to the selected semester page explicitly (avoid relative query-only redirects)
    return RedirectResponse(f"/year/{year}/semester/{semester}", status_code=303)


@subject_router.api_route(
    "/semester/{semester}/subject/{code}/prerequisite/add",
    methods=["POST", "GET", "HEAD"],
    response_class=RedirectResponse,
)
def add_prerequisite_route(
    request: Request,
    semester: str,
    code: str,
    year: str = Form(""),
    prerequisite_subject_id: Optional[str] = Form(None),
    custom_prerequisite: Optional[str] = Form(None),
    is_corequisite: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Add a prerequisite relationship for a subject.

    - POST performs the add and redirects back to the canonical subject page.
    - GET/HEAD simply redirect back without side effects (for safety/health checks).
    """
    # For non-POST methods, just redirect back without mutating state
    if request.method != "POST":
        target_year = year or str(request.query_params.get("year") or "")
        return RedirectResponse(
            url=f"/year/{target_year}/semester/{semester}/subject/{code}",
            status_code=303,
        )

    status = add_prerequisite_core(
        session=session,
        semester=semester,
        year=year,
        code=code,
        prerequisite_subject_id=prerequisite_subject_id,
        custom_prerequisite=custom_prerequisite,
        is_corequisite=is_corequisite,
    )

    if status == "semester_not_found":
        return RedirectResponse(
            url=f"/year/{year}/semester/{semester}/subject/{code}?error=Semester+not+found",
            status_code=303,
        )
    if status == "subject_not_found":
        return RedirectResponse(
            url=f"/year/{year}/semester/{semester}/subject/{code}?error=Subject+not+found",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/year/{year}/semester/{semester}/subject/{code}",
        status_code=303,
    )


@subject_router.api_route(
    "/year/{year}/semester/{semester}/subject/{code}/prerequisite/remove",
    methods=["POST", "GET", "HEAD"],
    response_class=RedirectResponse,
)
def remove_prerequisite_route(
    request: Request,
    year: str,
    semester: str,
    code: str,
    prerequisite_id: Optional[str] = Form(None),
    is_corequisite: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Remove a prerequisite relationship for a subject.

    - POST performs the removal via SubjectPrerequisiteManager.
    - GET/HEAD simply redirect back without side effects.
    """
    if request.method != "POST":
        return RedirectResponse(
            url=f"/year/{year}/semester/{semester}/subject/{code}",
            status_code=303,
        )

    try:
        year_int = int(str(year))
    except Exception:
        year_int = None

    sem = None
    if year_int is not None:
        sem = session.exec(
            select(Semester).where(
                Semester.name == semester,
                Semester.year == year_int,
            )
        ).first()

    if not sem or getattr(sem, "id", None) is None:
        return RedirectResponse(
            url=f"/year/{year}/semester/{semester}/subject/{code}?error=Semester+not+found",
            status_code=303,
        )

    if prerequisite_id:
        try:
            pid = int(prerequisite_id)
            prereq = session.get(SubjectPrerequisite, pid)
            if prereq is not None:
                session.delete(prereq)
                session.commit()
        except Exception:
            pass

    return RedirectResponse(
        url=f"/year/{year}/semester/{semester}/subject/{code}",
        status_code=303,
    )


@subject_router.api_route("/semester/{semester}/subject/{code}", methods=["GET", "HEAD"], response_class=RedirectResponse)
def subject_detail_legacy(
    request: Request,
    semester: str,
    code: str,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Legacy path: redirect to canonical /year/{year}/semester/{semester}/subject/{code}.

    This keeps old bookmarks/links working while the main
    subject detail rendering lives under the pretty URL
    handled in views.subject_detail_pretty.
    """
    year = request.query_params.get("year", "")
    return RedirectResponse(
        url=f"/year/{year}/semester/{semester}/subject/{code}",
        status_code=303,
    )

@subject_router.api_route("/semester/{semester}/subject/{code}/update", methods=["POST"], response_class=RedirectResponse)
def update_subject(
    semester: str,
    code: str,
    year: str = Form(...),
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    credit_points: int = Form(6),
    has_exam: Optional[bool] = Form(None),
    sync_subject: Optional[bool] = Form(False),
    old_semester: Optional[str] = Form(None),
    old_year: Optional[str] = Form(None),
    old_subject_code: Optional[str] = Form(None),
    return_to: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Update subject details."""
    # Use old values if provided (for moving subjects between semesters/years)
    search_semester = old_semester if old_semester else semester
    search_year = old_year if old_year else year
    search_code = old_subject_code if old_subject_code else code
    
    subject = session.exec(
        select(Subject).join(Semester,  expression.true() & (Subject.semester_id == Semester.id)).where(
            Semester.name == search_semester,
            Semester.year == int(search_year),
            Subject.subject_code == search_code
        )
    ).first()
    
    if subject:
        # Check for prerequisite violations if the subject is being moved
        is_moving = semester != search_semester or int(year) != int(search_year)
        if is_moving:
            violation_message = check_prerequisite_violations(
                session,
                subject,
                semester,
                int(year)
            )
            if violation_message:
                # Redirect back with error message
                return RedirectResponse(
                    url=f"/year/{search_year}/semester/{search_semester}/subject/{search_code}?error={violation_message}",
                    status_code=303,
                )
        
        # Find or create the target semester if it's different
        target_semester = None
        if is_moving:
            target_semester = session.exec(
                select(Semester).where(
                    Semester.name == semester,
                    Semester.year == int(year)
                )
            ).first()
            if target_semester and target_semester.id is not None:
                subject.semester_id = target_semester.id
        
        subject.subject_code = subject_code
        subject.subject_name = subject_name
        subject.credit_points = credit_points
        subject.sync_subject = bool(sync_subject)
        # Handle has_exam checkbox: if not present, set to False
        subject.has_exam = bool(has_exam)
        session.add(subject)
        session.commit()
        session.refresh(subject)
        # If subject code changed, we need to redirect to the new code
        new_code = subject.subject_code
    else:
        new_code = code

    # Redirect logic: if return_to encodes a semester context (e.g., "Autumn-2025"), go back there; else go to subject page
    if return_to:
        parts = str(return_to).split('-')
        if len(parts) == 2:
            return RedirectResponse(url=f"/year/{parts[1]}/semester/{parts[0]}", status_code=303)
    url = f"/year/{year}/semester/{semester}/subject/{new_code}"
    if return_to:
        url += f"?return_to={return_to}"
    return RedirectResponse(url=url, status_code=303)


@subject_router.api_route("/semester/{semester}/subject/{code}/delete", methods=["POST"], response_class=RedirectResponse)
def delete_subject(
    semester: str,
    code: str,
    year: str = Form(...),
    return_to: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Delete a subject and all its related data."""
    # Find the semester first to get its ID
    sem = session.exec(
        select(Semester).where(
            Semester.name == semester,
            Semester.year == int(year),
        )
    ).first()
    
    if not sem:
        # Semester not found, redirect with error
        return RedirectResponse(f"/year/{year}/semester/{semester}?error=Semester+not+found", status_code=303)
    
    # Find the subject by semester_id and code
    subject = session.exec(
        select(Subject).where(
            Subject.semester_id == sem.id,
            Subject.subject_code == code
        )
    ).first()
    
    if subject:
        # Delete related data (assignments, exams, settings)
        sid = getattr(subject, "id", None)
        if sid:
            assignments = session.exec(select(Assignment).where(Assignment.subject_id == sid)).all()
            for a in assignments:
                session.delete(a)
            exams = session.exec(select(Examination).where(Examination.subject_id == sid)).all()
            for e in exams:
                session.delete(e)
            settings = session.exec(select(ExamSettings).where(ExamSettings.subject_id == sid)).all()
            for s in settings:
                session.delete(s)
        session.delete(subject)
        session.commit()
    
    # Redirect
    if return_to:
        parts = return_to.split('-')
        if len(parts) == 2:
            return RedirectResponse(f"/year/{parts[1]}/semester/{parts[0]}", status_code=303)
    
    return RedirectResponse(f"/year/{year}/semester/{semester}", status_code=303)

@subject_router.get("/subjects/{year}/{code}")
def get_subject(
    year: str,
    code: str,
    semester: str,
    request: Request,
    session: Session = Depends(get_session),
):
    ctx = build_subject_page_context(session, semester=semester, year=year, code=code)
    if ctx is None:
        return RedirectResponse(
            f"/year/{year}/semester/{semester}?error=Subject+not+found",
            status_code=303,
        )

    return templates.TemplateResponse("subject.html", {"request": request, **ctx})
