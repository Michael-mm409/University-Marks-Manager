from typing import Optional
from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from src.infrastructure.db.engine import get_session
from src.infrastructure.db.models import Assignment, ExamSettings, Examination, GradeType

exam_router = APIRouter()

@exam_router.api_route("/totalMark/save", methods=["POST"], response_class=RedirectResponse)
def save_total_mark(
    semester: str,
    code: str,
    year: str = Form(...),
    total_mark: Optional[str] = Form(""),  # desired total final percentage
    exam_mark: Optional[str] = Form(""),   # fallback legacy field
    ps_exam: Optional[str] = Form(None),
    ps_factor: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
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

    # Determine exam weight (existing or inferred remaining)
    current_exam_weight = existing.exam_weight if existing else 0.0
    if not current_exam_weight:
        current_exam_weight = max(0.0, 100.0 - assignment_weight_percent)

    derived_exam_mark: float = 0.0

    if total_mark:
        try:
            goal = float(total_mark)
        except ValueError:
            goal = None
        # Determine effective scoring weight with PS scaling if requested
        ps_enabled = bool(ps_exam)
        scaling = 1.0
        if ps_enabled:
            try:
                scaling = (float(ps_factor) if ps_factor else 40.0) / 100.0
            except ValueError:
                scaling = 0.4
        # Persist/retrieve settings
        setting = session.exec(
            select(ExamSettings).where(
                ExamSettings.semester_name == semester,
                ExamSettings.year == year,
                ExamSettings.subject_code == code,
            )
        ).first()
        ps_enabled = bool(ps_exam)
        factor_val = 40.0
        if ps_factor:
            try:
                factor_val = float(ps_factor)
            except ValueError:
                factor_val = 40.0
        if not setting:
            setting = ExamSettings(
                subject_code=code,
                semester_name=semester,
                year=year,
                ps_exam=ps_enabled,
                ps_factor=factor_val,
            )
            session.add(setting)
        else:
            setting.ps_exam = ps_enabled
            setting.ps_factor = factor_val
        scaling = (factor_val / 100.0) if ps_enabled else 1.0
        scoring_weight = current_exam_weight * scaling if ps_enabled else current_exam_weight
        if goal is not None and 0 < goal <= 100 and scoring_weight > 0:
            needed_exam = (
                (goal / 100.0) * (assignment_weight_percent + scoring_weight) - assignment_weighted_sum
            ) * 100.0 / scoring_weight
            if needed_exam < 0:
                needed_exam = 0.0
            if needed_exam > 100:
                needed_exam = 100.0  # cap; UI can show impossible if desired
            derived_exam_mark = round(needed_exam, 4)
    # Legacy direct exam_mark override if provided and numeric
    if exam_mark:
        try:
            derived_exam_mark = float(exam_mark)
        except ValueError:
            pass

    if existing:
        existing.exam_mark = derived_exam_mark
        if not existing.exam_weight:
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
    session.commit()
    # Redirect without legacy ps_exam query params; state now persisted
    return RedirectResponse(
        f"?year={year}&total_mark={total_mark}", status_code=303
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
