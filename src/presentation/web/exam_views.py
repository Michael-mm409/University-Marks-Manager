from typing import Optional
from fastapi import Request
from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from src.infrastructure.db.engine import get_session
from src.infrastructure.db.models import Assignment, ExamSettings, Examination, GradeType, Subject

exam_router = APIRouter()

@exam_router.api_route("/totalMark/save", methods=["POST"], response_class=RedirectResponse)
def save_total_mark(
    request: Request,
    semester: str,
    code: str,
    year: str = Form(...),
    total_mark: Optional[str] = Form(""),  # desired total final percentage
    exam_mark: Optional[str] = Form(""),   # fallback legacy field
    ps_exam: Optional[str] = Form(None),
    ps_factor: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """Create or update exam using desired total mark input.

    If user supplies a desired overall final percentage (total_mark), derive the
    implied exam mark needed given current assignment contributions and exam weight.
    If exam_mark provided explicitly (legacy), that value is stored instead.
    """
    # Fetch existing exam (single allowed)
    existing = session.exec(
        select(Examination).where(
            Examination.semester_name == semester,
            Examination.year == year,
            Examination.subject_code == code,
        )
    ).first()

    # Aggregate assignment weighted marks and weight percent
    assignments = session.exec(
        select(Assignment).where(
            Assignment.semester_name == semester,
            Assignment.year == year,
            Assignment.subject_code == code,
        )
    ).all()
    assignment_weight_percent = 0.0
    assignment_weighted_sum = 0.0
    for a in assignments:
        if a.grade_type == GradeType.NUMERIC.value and a.mark_weight and a.weighted_mark:
            try:
                assignment_weight_percent += float(a.mark_weight)
                assignment_weighted_sum += float(a.weighted_mark)
            except ValueError:
                pass

    # Always calculate exam weight as remaining percentage
    current_exam_weight = max(0.0, 100.0 - assignment_weight_percent)

    # Always persist exam mark and exam weight, regardless of total_mark
    # If total_mark is provided, calculate derived_exam_mark, else keep previous or set to 0 if new
    ps_enabled = bool(ps_exam)
    factor_val = 40.0
    if ps_factor:
        try:
            factor_val = float(ps_factor)
        except ValueError:
            factor_val = 40.0
    if ps_enabled:
        scaling = factor_val / 100.0
        derived_exam_mark = current_exam_weight * scaling
    else:
        # For non-PS exams, required exam mark is total_mark - assignment_weighted_sum
        try:
            goal = float(total_mark) if total_mark else 0.0
        except ValueError:
            goal = 0.0
        derived_exam_mark = goal - assignment_weighted_sum

    # Always set exam_mark and exam_weight, regardless of whether it affects total_mark
    print(f"[DEBUG] Saving exam_mark for subject {code}: derived_exam_mark={derived_exam_mark}, exam_weight={current_exam_weight}, total_mark={total_mark}, assignment_weighted_sum={assignment_weighted_sum}, assignment_weight_percent={assignment_weight_percent}, ps_exam={ps_exam}, ps_factor={ps_factor}")
    if existing:
        existing.exam_mark = derived_exam_mark
        existing.exam_weight = current_exam_weight
    else:
        new_exam = Examination(
            subject_code=code,
            semester_name=semester,
            year=year,
            exam_mark=derived_exam_mark,
            exam_weight=current_exam_weight,
        )
        session.add(new_exam)

    # Save total_mark to Subject so it persists and displays correctly
    subject = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
        )
    ).first()
    if subject:
        # Only update total_mark from the form, do not let exam_mark affect it
        if total_mark:
            try:
                subject.total_mark = float(total_mark)
            except ValueError:
                subject.total_mark = None
        else:
            subject.total_mark = None
        session.add(subject)
    session.commit()

    # Return JSON if AJAX, else redirect
    def is_ajax(request):
        try:
            return request.headers.get("X-Requested-With") == "XMLHttpRequest"
        except Exception:
            return False

    if is_ajax(request):
        from fastapi.responses import JSONResponse
        return JSONResponse({"success": True, "exam_mark": derived_exam_mark, "exam_weight": current_exam_weight})
    else:
        return RedirectResponse(
            f"/semester/{semester}/subject/{code}?year={year}", status_code=303
        )


@exam_router.api_route("/exam/{exam_id}/delete", methods=["POST"], response_class=RedirectResponse)
def delete_exam(
    semester: str,
    code: str,
    exam_id: int,
    year: str = Form(...),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Delete the examination record for a subject (single exam model)."""
    existing = session.get(Examination, exam_id)
    if existing and existing.subject_code == code and existing.semester_name == semester and existing.year == year:
        session.delete(existing)
        session.commit()
    return RedirectResponse(
        f"?year={year}", status_code=303
    )
