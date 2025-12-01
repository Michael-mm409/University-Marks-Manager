from typing import Optional
from fastapi import Request
from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
import logging

from src.infrastructure.db.engine import get_session
from src.infrastructure.db.models import Assignment, ExamSettings, Examination, GradeType, Subject

logger = logging.getLogger("uvicorn.error")
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
    return_to: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """Create or update exam using desired total mark input.

    If user supplies a desired overall final percentage (total_mark), derive the
    implied exam mark needed given current assignment contributions and exam weight.
    If exam_mark provided explicitly (legacy), that value is stored instead.
    """
    logger.info(f"[DEBUG] POST data: semester={semester}, code={code}, year={year}, total_mark={total_mark}, exam_mark={exam_mark}, ps_exam={ps_exam}, ps_factor={ps_factor}, return_to={return_to}")

   
    # Resolve subject_id for normalized lookups
    subj = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
        )
    ).first()
    sid = getattr(subj, "id", None)
    logger.info(f"[DEBUG] Looked up subject_id: {sid} for subject_code={code}, semester={semester}, year={year}")
    # Fetch existing exam (single allowed)
    existing = session.exec(
        select(Examination).where(
            Examination.subject_id == sid
        )
    ).first()
    logger.info(f"[DEBUG] Existing exam row: {existing}")

    # Aggregate assignment weighted marks and weight percent
    assignments = session.exec(
        select(Assignment).where(
            Assignment.subject_id == sid
        ).order_by(Assignment.assessment)
    ).all()
    assignment_weight_percent = 0.0
    assignment_weighted_sum = 0.0
    # Log all assignments and their details for debugging
    if assignments:
        logger.info(f"[DEBUG] Assignments for subject {code} ({semester} {year}):")
        for a in assignments:
            logger.info(f"[DEBUG]   - Assessment: {getattr(a, 'assessment', None)}, Name: {getattr(a, 'name', None)}, Mark: {getattr(a, 'mark', None)}, Weight: {getattr(a, 'mark_weight', None)}, Weighted Mark: {getattr(a, 'weighted_mark', None)}, Grade Type: {getattr(a, 'grade_type', None)}")
    else:
        logger.info(f"[DEBUG] No assignments found for subject {code} ({semester} {year})")
    for a in assignments:
        if a.grade_type == GradeType.NUMERIC.value and a.mark_weight and a.weighted_mark:
            try:
                assignment_weight_percent += float(a.mark_weight)
                assignment_weighted_sum += float(a.weighted_mark)
            except ValueError:
                pass
    logger.info(f"[DEBUG] assignment_weight_percent={assignment_weight_percent}, assignment_weighted_sum={assignment_weighted_sum}")


    # Always calculate exam weight as remaining percentage
    current_exam_weight = max(0.0, 100.0 - assignment_weight_percent)
    logger.info(f"[DEBUG] current_exam_weight={current_exam_weight}")

    # Always persist exam mark and exam weight, regardless of total_mark
    # If total_mark is provided, calculate derived_exam_mark, else keep previous or set to 0 if new
    ps_enabled = bool(ps_exam)
    factor_val = 40.0
    if ps_factor:
        try:
            factor_val = float(ps_factor)
        except ValueError:
            factor_val = 40.0
    scaling = factor_val / 100.0 if ps_enabled else 1.0
    effective_exam_weight = current_exam_weight * scaling if ps_enabled else current_exam_weight
    logger.info(f"[DEBUG] ps_enabled={ps_enabled}, factor_val={factor_val}, scaling={scaling}, effective_exam_weight={effective_exam_weight}")


    goal = None
    if total_mark not in (None, ""):
        try:
            goal = float(total_mark)
        except ValueError:
            goal = None

    # mark_to_save will be set below based on PS logic
    if goal is not None and effective_exam_weight:
        needed_weighted = (goal / 100.0) * (assignment_weight_percent + effective_exam_weight) - assignment_weighted_sum
        logger.info(f"[DEBUG] needed_weighted={needed_weighted}")
        derived_exam_mark = (needed_weighted * 100.0) / effective_exam_weight
        logger.info(f"[DEBUG] derived_exam_mark (from goal)={derived_exam_mark}")
    elif exam_mark not in (None, ""):
        try:
            derived_exam_mark = float(exam_mark)
            logger.info(f"[DEBUG] derived_exam_mark (from manual input)={derived_exam_mark}")
        except ValueError:
            derived_exam_mark = None
    else:
        # No target or manual mark: set to available mark (PS Factor × exam weight, or exam weight)
        derived_exam_mark = current_exam_weight * scaling
        logger.info(f"[DEBUG] derived_exam_mark (fallback)={derived_exam_mark}")

    # Clamp exam mark to [0, 100] and ensure it's a float
    if derived_exam_mark is None:
        derived_exam_mark = 0.0
    derived_exam_mark = float(derived_exam_mark)
    derived_exam_mark = max(0.0, min(100.0, derived_exam_mark))

    # For PS exams, save the weighted exam mark as exam_weight * ps_factor (as a fraction)
    if ps_enabled:
        mark_to_save = current_exam_weight * scaling
    else:
        mark_to_save = derived_exam_mark
    logger.info(f"[DEBUG] mark_to_save={mark_to_save}, exam_weight={current_exam_weight}, total_mark={total_mark}, assignment_weighted_sum={assignment_weighted_sum}, assignment_weight_percent={assignment_weight_percent}, ps_exam={ps_exam}, ps_factor={ps_factor}")
    # Resolve subject to set subject_id for normalized schema
    if existing:
        existing.exam_mark = mark_to_save
        existing.exam_weight = current_exam_weight
        # Ensure subject_id is set (legacy rows are backfilled, but be defensive)
        if getattr(existing, "subject_id", None) is None and sid is not None:
            existing.subject_id = sid
    else:
        new_exam = Examination(
            subject_id=sid,
            subject_code=code,
            semester_name=semester,
            year=year,
            exam_mark=mark_to_save,
            exam_weight=current_exam_weight,
        )
        session.add(new_exam)

    # Update or create ExamSettings for PS Exam
    settings = session.exec(
        select(ExamSettings).where(
            ExamSettings.subject_id == sid
        )
    ).first()
    ps_exam_bool = bool(ps_exam)
    ps_factor_val = factor_val
    if settings:
        settings.ps_exam = ps_exam_bool
        settings.ps_factor = ps_factor_val
        session.add(settings)
    else:
        new_settings = ExamSettings(
            subject_id=sid,
            subject_code=code,
            semester_name=semester,
            year=year,
            ps_exam=ps_exam_bool,
            ps_factor=ps_factor_val
        )
        session.add(new_settings)

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
        """
        Short description.

        Args:
            request: Description.

        Raises:
            Description.
        """
        try:
            return request.headers.get("X-Requested-With") == "XMLHttpRequest"
        except Exception:
            return False

    if is_ajax(request):
        from fastapi.responses import JSONResponse
        return JSONResponse({"success": True, "exam_mark": derived_exam_mark, "exam_weight": current_exam_weight})
    else:
        url = f"/semester/{semester}/subject/{code}?year={year}"
        if total_mark not in (None, ""):
            url += f"&total_mark={total_mark}"
        if return_to:
            url += f"&return_to={return_to}"
        return RedirectResponse(url, status_code=303)


@exam_router.api_route("/exam/{exam_id}/delete", methods=["POST"], response_class=RedirectResponse)
def delete_exam(
    semester: str,
    code: str,
    exam_id: int,
    year: str = Form(...),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Delete the examination record for a subject (single exam model)."""
    # Prefer normalized lookup by subject_id; fallback to composite key for legacy rows
    subj = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
        )
    ).first()
    sid = getattr(subj, "id", None)
    existing = None
    if sid is not None:
        existing = session.exec(select(Examination).where(Examination.subject_id == sid)).first()
    if not existing:
        existing = session.get(Examination, (code, semester, year))
    if existing:
        session.delete(existing)
        session.commit()
    return RedirectResponse(
        f"?year={year}", status_code=303
    )
