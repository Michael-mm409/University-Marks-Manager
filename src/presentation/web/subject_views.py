from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from typing import Optional, cast
from sqlalchemy import Table
from fastapi import Request
from src.presentation.api.deps import get_session
from src.infrastructure.db.models import Subject, Assignment, Examination, ExamSettings, GradeType, Semester
from .types import SubjectContext

subject_router = APIRouter()

@subject_router.api_route("/subject/create", methods=["POST"])
def create_subject(
    semester: str,
    year: str = Form(...),
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    credit_points: int = Form(6),
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
        # Resolve semester_id for normalized schema
        sem = session.exec(
            select(Semester).where(
                Semester.name == semester,
                Semester.year == int(year) if str(year).isdigit() else Semester.year == Semester.year,
            )
        ).first()
        semester_id = getattr(sem, "id", None)
        session.add(
            Subject(
                semester_id=semester_id,
                subject_code=subject_code,
                subject_name=subject_name,
                semester_name=semester,
                year=year,
                credit_points=credit_points,
                sync_subject=bool(sync_subject),
            )
        )
        session.commit()
    return RedirectResponse(f"?year={year}", status_code=303)


def build_subject_context(
    session: Session,
    semester: str,
    year: str,
    code: str,
    exam_weight: Optional[float] = None,
    final_total: Optional[str] = None,
    total_mark: Optional[str] = None,
    return_to: Optional[str] = None,
) -> Optional[SubjectContext]:
    """Build the SubjectContext for rendering the subject detail page."""
    subject = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
        )
    ).first()
    if not subject:
        return None

    # Now that the DB has surrogate keys, prefer subject_id for child lookups
    sid = getattr(subject, "id", None)
    # Order assignments by their numeric id so the UI shows them in creation/order sequence
    # Use .asc() to produce a SQL expression that static type-checkers (Pylance) accept
    # Use the model's Table column expression so static checkers see a SQL column element
    # Use a typed Table reference so static analysers (Pylance) accept the column accessl
    assignments_table = cast(Table, getattr(Assignment, "__table__"))
    assignments = session.exec(
        select(Assignment).where(
            Assignment.subject_id == sid
        ).order_by(assignments_table.columns.id.asc())
    ).all()
    examinations = session.exec(
        select(Examination).where(
            Examination.subject_id == sid
        )
    ).all()

    assignment_weighted_sum = 0.0
    assignment_weight_percent = 0.0
    
    count_s = 0
    count_u = 0

    # Identify assignment-based exam
    exam_assignment = next((a for a in assignments if getattr(a, "is_exam", False)), None)

    for assignment_record in assignments:
        if assignment_record.grade_type == GradeType.SATISFACTORY.value:
            count_s += 1
        elif assignment_record.grade_type == GradeType.UNSATISFACTORY.value:
            count_u += 1

        if getattr(assignment_record, "is_exam", False):
            continue

        if (
            assignment_record.grade_type == GradeType.NUMERIC.value
            and assignment_record.weighted_mark is not None
            and assignment_record.mark_weight is not None
        ):
            try:
                assignment_weighted_sum += float(assignment_record.weighted_mark)
                assignment_weight_percent += float(assignment_record.mark_weight)
            except (TypeError, ValueError):
                pass

    exam_raw_percent: Optional[float] = None
    exam_contribution = 0.0
    existing_exam_weight = 0.0
    
    # Legacy exam data
    single_exam = examinations[0] if examinations else None
    legacy_exam_mark: Optional[float] = None
    legacy_exam_weight: float = 0.0

    if single_exam:
        try:
            legacy_exam_mark = float(single_exam.exam_mark)
        except (TypeError, ValueError):
            pass
        try:
            legacy_exam_weight = float(single_exam.exam_weight)
        except (TypeError, ValueError):
            pass

    # Determine active exam source
    if exam_assignment:
        # Use assignment based exam
        # Assignment stores unweighted_mark as a ratio (e.g. 0.75 for 75%), so we multiply by 100 for percent logic
        if exam_assignment.unweighted_mark is not None:
             exam_raw_percent = float(exam_assignment.unweighted_mark) * 100.0
        
        if exam_assignment.mark_weight is not None:
            existing_exam_weight = float(exam_assignment.mark_weight)
            
    elif single_exam:
        # Fallback to legacy
        exam_raw_percent = legacy_exam_mark
        existing_exam_weight = legacy_exam_weight

    inferred_remaining = 0.0
    if not exam_assignment and not examinations:
        inferred_remaining = max(0.0, 100.0 - assignment_weight_percent)

    # Always calculate exam weight as 100 - assignment_weight_percent for summary
    effective_exam_weight = 100.0 - assignment_weight_percent
    setting = session.exec(
        select(ExamSettings).where(
            ExamSettings.subject_id == sid
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

    desired_goal = None
    if final_total not in (None, ""):
        desired_goal = final_total
    elif total_mark not in (None, ""):
        desired_goal = total_mark
    elif subject.total_mark not in (None, 0, 0.0):
        desired_goal = str(subject.total_mark)
    
    if desired_goal is not None:
        try:
            goal = float(desired_goal)
            if goal <= 0 or goal > 100:
                requirement_status = "invalid"
            else:
                is_exam_taken = exam_raw_percent is not None and exam_raw_percent > 0
                effective_exam_score = effective_scoring_exam_weight
                if effective_exam_score > 0:
                    # Calculate required exam mark as a percentage of the scaled exam weight
                    required_exam_mark = ((goal - assignment_weighted_sum) / effective_exam_score) * 100.0
                    # Clamp to 0–100
                    if required_exam_mark < 0:
                        required_exam_mark = 0.0
                    elif required_exam_mark > 100:
                        required_exam_mark = 100.0
                if average is not None and is_exam_taken and average >= goal:
                    requirement_status = "achieved"
                else:
                    if effective_exam_score <= 0:
                        requirement_status = "impossible"
                    elif required_exam_mark is not None:
                        if required_exam_mark == 0:
                            requirement_status = "achieved"
                        elif required_exam_mark == 100:
                            requirement_status = "impossible"
                        else:
                            requirement_status = "feasible"
                        if requirement_status in ("feasible", "achieved"):
                            projected_total_weighted = round(goal, 2)
        except ValueError:
            requirement_status = "invalid"


    # For summary: if there is an assignment-based exam, use its mark; otherwise, use the Examination table value
    import logging
    logger = logging.getLogger("uvicorn.error")
    summary_exam_mark = None
    if exam_assignment and hasattr(exam_assignment, "weighted_mark") and exam_assignment.weighted_mark is not None:
        summary_exam_mark = float(exam_assignment.weighted_mark)
        logger.info(f"[DEBUG] Using assignment-based exam mark for summary: {summary_exam_mark}")
    elif single_exam and single_exam.exam_mark is not None:
        summary_exam_mark = float(single_exam.exam_mark)
        logger.info(f"[DEBUG] Using Examination table exam mark for summary: {summary_exam_mark}")

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
        "exam_mark": summary_exam_mark,
        "assignment_weighted_sum": round(assignment_weighted_sum, 2),
        "assignment_weight_percent": round(assignment_weight_percent, 2),
        "exam_weighted_sum": round(exam_contribution, 2),
        "effective_scoring_exam_weight": round(effective_scoring_exam_weight, 2),
        "return_to": return_to,
        "legacy_exam_mark": legacy_exam_mark,
        "legacy_exam_weight": legacy_exam_weight,
        "has_legacy_exam": bool(single_exam),
        "has_assignment_exam": bool(exam_assignment),
        "count_s": count_s,
        "count_u": count_u,
        "final_exam_mark_weight": round(effective_exam_weight, 2),
        "summary_exam_mark": summary_exam_mark,
    }
    return ctx


@subject_router.api_route("/subject/{code}", methods=["GET", "HEAD"], response_class=RedirectResponse)
def subject_detail(
    semester: str,
    code: str,
    year: str,
) -> RedirectResponse:
    """Legacy path: redirect to the short subject URL (/subjects/{year}/{code}?semester=...)."""
    return RedirectResponse(url=f"/subjects/{year}/{code}?semester={semester}", status_code=303)


@subject_router.api_route("/subject/{code}/update", methods=["POST"], response_class=RedirectResponse)
def update_subject(
    semester: str,
    code: str,
    year: str = Form(...),
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    credit_points: int = Form(6),
    return_to: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Update subject details."""
    subject = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
        )
    ).first()
    
    if subject:
        subject.subject_code = subject_code
        subject.subject_name = subject_name
        subject.credit_points = credit_points
        session.add(subject)
        session.commit()
        session.refresh(subject)
        
        # If subject code changed, we need to redirect to the new code
        new_code = subject.subject_code
    else:
        new_code = code

    # Redirect back to the subject page
    url = f"/subjects/{year}/{new_code}?semester={semester}"
    if return_to:
         url += f"&return_to={return_to}"

    return RedirectResponse(url=url, status_code=303)


@subject_router.api_route("/subject/{code}/delete", methods=["POST"], response_class=RedirectResponse)
def delete_subject(
    semester: str,
    code: str,
    year: str = Form(...),
    return_to: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Delete a subject and all its related data."""
    subject = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
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
