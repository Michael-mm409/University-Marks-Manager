from fastapi import Depends, Form, Request, APIRouter
from typing import List
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from src.presentation.api.deps import get_session
from src.infrastructure.db.models import Semester, Subject, Assignment, Examination, ExamSettings, GradeType
from .template_helpers import _render
semester_router = APIRouter()
from .types import SemesterSummary, SemesterContext

@semester_router.api_route("/create", methods=["POST"])
def create_semester(
    request: Request,
    name: str = Form(...),
    year: str = Form(...),
    return_year: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """
    Create a new semester if it does not already exist.
    
    Args:
        name (str): Semester name.
        year (str): Semester year.
        session (Session): Database session dependency.
    
    Returns:
        RedirectResponse: Redirect to home page.
    """

    # Ensure year is an int for comparisons and creation
    try:
        year_int = int(year)
    except Exception:
        year_int = int(str(year).strip())

    exists = session.exec(
        select(Semester).where(Semester.name == name, Semester.year == year_int)
    ).first()
    if not exists:
        # If a course is active, auto-link the new semester to that course
        course_id = request.session.get("current_course_id")
        try:
            cid = int(course_id) if course_id is not None else None
        except Exception:
            cid = None
        session.add(Semester(name=name, year=year_int, course_id=cid))
        session.commit()
    else:
        # If the semester exists but is unassigned, and a course is active, link it
        if getattr(exists, "course_id", None) is None:
            course_id = request.session.get("current_course_id")
            try:
                cid = int(course_id) if course_id is not None else None
            except Exception:
                cid = None
            if cid is not None:
                exists.course_id = cid
                session.commit()
    # Redirect back to the filtered year if provided; otherwise use the semester's year
    target_year = (return_year or str(year_int)).strip() if str(return_year or "").strip() else str(year_int)
    return RedirectResponse(f"/?year={target_year}", status_code=303)


@semester_router.api_route("/{semester}/delete", methods=["POST"])
def delete_semester(
    semester: str,
    year: str = Form(...),
    return_year: str | None = Form(default=None),
    session: Session = Depends(get_session),
):
    """Delete a semester and all related data."""
    # Delete assignments, exams, settings, subjects for that semester/year
    subs = session.exec(select(Subject).where(Subject.semester_name == semester, Subject.year == year)).all()
    for sub in subs:
        session.exec(
            select(Assignment).where(
                Assignment.semester_name == semester,
                Assignment.year == year,
                Assignment.subject_code == sub.subject_code,
            ).order_by(Assignment.assessment)
        )  # placeholder retrieval (deletion with ORM objects below)
    # Direct delete via ORM load (simpler for small dataset)
    assignments = session.exec(select(Assignment).where(Assignment.semester_name == semester, Assignment.year == year)).all()
    exams = session.exec(select(Examination).where(Examination.semester_name == semester, Examination.year == year)).all()
    settings = session.exec(select(ExamSettings).where(ExamSettings.semester_name == semester, ExamSettings.year == year)).all()
    # Delete each collection explicitly (avoids type checker complaints about '+' on heterogeneous sequences)
    for obj in assignments:
        session.delete(obj)
    for obj in exams:
        session.delete(obj)
    for obj in settings:
        session.delete(obj)
    for obj in subs:
        session.delete(obj)
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == year)).first()
    if sem:
        session.delete(sem)
    session.commit()
    # Preserve selected filter year if provided
    target_year = (return_year or year).strip() if str(return_year or "").strip() else str(year)
    return RedirectResponse(f"/?year={target_year}", status_code=303)


@semester_router.api_route("/{semester}/update", methods=["POST"])
def update_semester(
    semester: str,
    year: str = Form(...),
    new_name: str = Form(...),
    return_year: str | None = Form(default=None),
    session: Session = Depends(get_session),
):
    """Rename a semester and preserve the current year filter on redirect.

    Redirects back to Home with ?year=<year> so the filtered view remains active.
    """
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == year)).first()
    if sem:
        sem.name = new_name
        session.commit()
    # Preserve the filtered year the user was viewing if provided (fallback to the semester's year)
    target_year = (return_year or year).strip() if str(return_year or "").strip() else str(year)
    return RedirectResponse(f"/?year={target_year}", status_code=303)


@semester_router.api_route("/{semester}", response_class=HTMLResponse, methods=["GET", "HEAD"])
def semester_detail(
    request: Request,
    semester: str,
    year: str,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    """
    Render the semester detail page listing subjects in the semester/year with summary metrics.
    
    Args:
        request (Request): The incoming HTTP request.
        semester (str): Semester name.
        year (str): Semester year.
        session (Session): Database session dependency.
    
    Returns:
        HTMLResponse: Rendered semester detail page.
    """
    # Get all subjects for the year, including synced subjects from other semesters
    subjects = session.exec(
        select(Subject).where(Subject.year == year)
    ).all()
    # Only show subjects for the current semester and all synced subjects
    main_subjects = [s for s in subjects if s.semester_name == semester]
    synced_subjects = [s for s in subjects if s.sync_subject and s.semester_name != semester]
    display_subjects = main_subjects + synced_subjects
    summaries: List[SemesterSummary] = []
    for sub in display_subjects:
        # Use correct semester for assignments/exams
        assignments = session.exec(
            select(Assignment).where(
                Assignment.semester_name == sub.semester_name,
                Assignment.year == year,
                Assignment.subject_code == sub.subject_code,
            ).order_by(Assignment.assessment)
        ).all()
        exam = session.exec(
            select(Examination).where(
                Examination.semester_name == sub.semester_name,
                Examination.year == year,
                Examination.subject_code == sub.subject_code,
            )
        ).first()
        assess_weight_sum = 0.0
        assess_weighted_total = 0.0
        for a in assignments:
            if a.grade_type == GradeType.NUMERIC.value:
                # Always include the assignment's weight if present, even if not yet marked
                if a.mark_weight not in (None, ""):
                    try:
                        assess_weight_sum += float(a.mark_weight)
                    except ValueError:
                        pass
                # Only add to weighted total when a weighted mark exists
                if a.weighted_mark not in (None, ""):
                    try:
                        assess_weighted_total += float(a.weighted_mark)
                    except ValueError:
                        pass
        exam_mark = None
        exam_weight = None
        if exam:
            try:
                exam_mark = float(exam.exam_mark)
            except (TypeError, ValueError):
                exam_mark = None
            try:
                exam_weight = float(exam.exam_weight)
            except (TypeError, ValueError):
                exam_weight = None
        # Use the saved total_mark from the database
        total_mark = sub.total_mark if sub.total_mark not in (None, 0) else None
        summaries.append(
            {
                "code": sub.subject_code,
                "name": sub.subject_name,
                "semester_name": sub.semester_name,
                "assessment_mark": round(assess_weighted_total, 2),
                "assessment_weight": assess_weight_sum,
                "exam_mark": exam_mark,
                "exam_weight": exam_weight,
                "total_mark": total_mark,
                "sync_subject": sub.sync_subject,
            }
        )

    ctx: SemesterContext = {
        "semester": semester,
        "year": year,
        "subjects": display_subjects,
        "subject_summaries": summaries,
    }

    return _render(request, "semester.html", ctx)
