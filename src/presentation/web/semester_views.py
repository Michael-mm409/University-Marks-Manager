from fastapi import Depends, Form, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from src.presentation.api.deps import get_session
from src.infrastructure.db.models import Semester, Subject, Assignment, Examination, ExamSettings, GradeType
from .template_helpers import _render
semester_router = APIRouter()

@semester_router.api_route("/create", methods=["POST"])
def create_semester(
    name: str = Form(...),
    year: str = Form(...),
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

    exists = session.exec(
        select(Semester).where(Semester.name == name, Semester.year == year)
    ).first()
    if not exists:
        session.add(Semester(name=name, year=year))
        session.commit()
    return RedirectResponse("/", status_code=303)


@semester_router.api_route("/{semester}/delete", methods=["POST"])
def delete_semester(semester: str, year: str = Form(...), session: Session = Depends(get_session)):
    """Delete a semester and all related data."""
    # Delete assignments, exams, settings, subjects for that semester/year
    subs = session.exec(select(Subject).where(Subject.semester_name == semester, Subject.year == year)).all()
    for sub in subs:
        session.exec(
            select(Assignment).where(
                Assignment.semester_name == semester,
                Assignment.year == year,
                Assignment.subject_code == sub.subject_code,
            )
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
    return RedirectResponse("/", status_code=303)


@semester_router.api_route("/{semester}/update", methods=["POST"])
def update_semester(semester: str, year: str = Form(...), new_name: str = Form(...), session: Session = Depends(get_session)):
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == year)).first()
    if sem:
        sem.name = new_name
        session.commit()
    return RedirectResponse("/", status_code=303)


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
    subjects = session.exec(
        select(Subject).where(Subject.semester_name == semester, Subject.year == year)
    ).all()
    # Build summary rows similar to provided screenshot
    summaries = []
    for sub in subjects:
        assignments = session.exec(
            select(Assignment).where(
                Assignment.semester_name == semester,
                Assignment.year == year,
                Assignment.subject_code == sub.subject_code,
            )
        ).all()
        exam = session.exec(
            select(Examination).where(
                Examination.semester_name == semester,
                Examination.year == year,
                Examination.subject_code == sub.subject_code,
            )
        ).first()
        assess_weight_sum = 0.0
        assess_weighted_total = 0.0
        for a in assignments:
            if a.grade_type == GradeType.NUMERIC.value and a.mark_weight and a.weighted_mark:
                try:
                    assess_weight_sum += float(a.mark_weight)
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
        total_mark = None
        if assess_weight_sum or exam_weight:
            try:
                total_weighted = assess_weighted_total
                total_weight_percent = assess_weight_sum
                if exam_mark is not None and exam_weight is not None:
                    total_weighted += (exam_mark / 100.0) * exam_weight
                    total_weight_percent += exam_weight
                if total_weight_percent > 0:
                    total_mark = round((total_weighted / total_weight_percent) * 100.0, 2)
            except ZeroDivisionError:
                total_mark = None
        summaries.append(
            {
                "code": sub.subject_code,
                "name": sub.subject_name,
                "assessment_mark": round(assess_weighted_total, 2),
                "assessment_weight": assess_weight_sum,
                "exam_mark": exam_mark,
                "exam_weight": exam_weight,
                "total_mark": total_mark,
                "sync_subject": sub.sync_subject,
            }
        )
    return _render(
        request,
        "semester.html",
        {"semester": semester, "year": year, "subjects": subjects, "subject_summaries": summaries},
    )
