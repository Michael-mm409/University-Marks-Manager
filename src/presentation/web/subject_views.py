from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from typing import Optional
from fastapi import Request
from src.presentation.api.deps import get_session
from src.infrastructure.db.models import Subject, Assignment, Examination, ExamSettings, GradeType
from src.presentation.web.template_helpers import _render
from .types import SubjectContext

subject_router = APIRouter()

@subject_router.api_route("/subject/create", methods=["POST"])
def create_subject(
    semester: str,
    year: str = Form(...),
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    sync_subject: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """
    Create a new subject in the semester if it does not already exist.
    
    Args:
        semester (str): Semester name.
        year (str): Semester year.
        subject_code (str): Subject code.
        subject_name (str): Subject name.
        sync_subject (Optional[str]): Sync subject identifier.
        session (Session): Database session dependency.
        
    Returns:
        RedirectResponse: Redirect to semester detail page.
    """
    exists = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == subject_code,
        )
    ).first()
    if not exists:
        session.add(
            Subject(
                subject_code=subject_code,
                subject_name=subject_name,
                semester_name=semester,
                year=year,
                sync_subject=bool(sync_subject),
            )
        )
        session.commit()
    return RedirectResponse(f"?year={year}", status_code=303)


@subject_router.api_route("/subject/{code}", methods=["GET", "HEAD"], response_class=HTMLResponse)
def subject_detail(
    request: Request,
    semester: str,
    code: str,
    year: str,
    exam_weight: Optional[float] = None,
    final_total: Optional[str] = None,
    total_mark: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Render the subject detail page showing assignments, exams, and computed averages."""
    # Fetch the main subject
    subject = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
        )
    ).first()
    if not subject:
        return HTMLResponse("Subject not found", status_code=404)

    # Only get assignments and exams for the current subject (ordered alphabetically)
    assignments = session.exec(
        select(Assignment).where(
            Assignment.year == year,
            Assignment.subject_code == code,
        ).order_by(Assignment.assessment)
    ).all()
    examinations = session.exec(
        select(Examination).where(
            Examination.year == year,
            Examination.subject_code == code,
        )
    ).all()

    assignment_weighted_sum = 0.0
    assignment_weight_percent = 0.0
    for a in assignments:
        if a.grade_type == GradeType.NUMERIC.value and a.weighted_mark and a.mark_weight:
            try:
                assignment_weighted_sum += float(a.weighted_mark)
                assignment_weight_percent += float(a.mark_weight)
            except ValueError:
                pass

    exam_raw_percent: Optional[float] = None
    exam_contribution = 0.0
    existing_exam_weight = 0.0
    single_exam = examinations[0] if examinations else None
    if single_exam:
        try:
            exam_raw_percent = float(single_exam.exam_mark)
        except (TypeError, ValueError):
            exam_raw_percent = None
        try:
            existing_exam_weight = float(single_exam.exam_weight)
        except (TypeError, ValueError):
            existing_exam_weight = 0.0

    inferred_remaining = 0.0
    if not examinations:
        inferred_remaining = max(0.0, 100.0 - assignment_weight_percent)

    # Determine which exam weight to use for requirement calculations
    effective_exam_weight = (
        existing_exam_weight
        or (exam_weight if (exam_weight and not examinations) else inferred_remaining)
    )
    # PS exam scaling: user-defined factor (default 40%), expressed as percentage of exam weight contributing
    # Load persisted PS settings
    setting = session.exec(
        select(ExamSettings).where(
            ExamSettings.semester_name == semester,
            ExamSettings.year == year,
            ExamSettings.subject_code == code,
        )
    ).first()
    ps_exam = bool(setting.ps_exam) if setting else False
    parsed_factor = setting.ps_factor if setting else 40.0
    scaling = (parsed_factor / 100.0) if ps_exam else 1.0
    effective_scoring_exam_weight = effective_exam_weight * scaling

    if exam_raw_percent is not None and effective_scoring_exam_weight > 0:
        exam_contribution = (exam_raw_percent / 100.0) * effective_scoring_exam_weight

    total_weighted = assignment_weighted_sum + exam_contribution
    total_scoring_weight_percent = assignment_weight_percent + (
        effective_scoring_exam_weight if effective_scoring_exam_weight else 0.0
    )
    average = (
        round(total_weighted / total_scoring_weight_percent * 100, 2)
        if total_scoring_weight_percent
        else None
    )

    required_exam_mark: Optional[float] = None
    requirement_status: Optional[str] = None
    projected_total_weighted: Optional[float] = None

    # Allow user to pass either final_total (desired final percentage) or total_mark (alias)
    desired_goal = None
    if final_total not in (None, ""):
        desired_goal = final_total
    elif total_mark not in (None, ""):
        desired_goal = total_mark
    if desired_goal is not None:
        try:
            goal = float(desired_goal)
            if goal <= 0 or goal > 100:
                requirement_status = "invalid"
            else:
                # If we already have an exam mark and achieved goal
                if average is not None and exam_raw_percent is not None and average >= goal:
                    requirement_status = "achieved"
                else:
                    effective_exam_score = effective_scoring_exam_weight
                    if effective_exam_score <= 0:
                        requirement_status = "impossible"
                    else:
                        # Equation: (assign_sum + exam_required/100 * effective_exam_score) / (total_assignment_weight + effective_exam_score) * 100 = goal
                        required_exam_mark = (
                            (goal / 100.0) * (assignment_weight_percent + effective_exam_score) - assignment_weighted_sum
                        ) * 100.0 / effective_exam_score
                        if required_exam_mark < 0:
                            requirement_status = "achieved"
                        elif required_exam_mark > 100:
                            requirement_status = "impossible"
                        else:
                            requirement_status = "feasible"
                        if requirement_status in ("feasible", "achieved"):
                            projected_total_weighted = round(goal, 2)
        except ValueError:
            requirement_status = "invalid"

    return_to = request.query_params.get("return_to")

    ctx: SubjectContext = {
        "semester": semester,
        "year": year,
        "subject": subject,
        "assignments": assignments,
        "examinations": examinations,
        "total_weighted": round(total_weighted, 2),
        "projected_total_weighted": projected_total_weighted,
        "total_weight_percent": round(total_scoring_weight_percent, 2),
        "average": average,
        "final_total": desired_goal,
        "total_mark": desired_goal,
        "effective_exam_weight": effective_exam_weight,
        "required_exam_mark": None if required_exam_mark is None else round(required_exam_mark, 2),
        "requirement_status": requirement_status,
        "ps_exam": ps_exam,
        "ps_factor": parsed_factor if ps_exam else None,
        "raw_exam_percent": exam_raw_percent,
        "exam_mark": exam_raw_percent,
        "assignment_weighted_sum": round(assignment_weighted_sum, 2),
        "assignment_weight_percent": round(assignment_weight_percent, 2),
        "exam_weighted_sum": round(exam_contribution, 2),
        "effective_scoring_exam_weight": round(effective_scoring_exam_weight, 2),
        "return_to": return_to,
    }

    return _render(request, "subject.html", ctx)
