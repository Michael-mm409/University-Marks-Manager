from __future__ import annotations

from typing import List, Optional

from sqlmodel import col, Session, select

from src.core.services.subject_prerequisite_manager import SubjectPrerequisiteManager
from src.infrastructure.db.models import Assignment, Examination, ExamSettings
from src.presentation.web.utils.subject_helpers import resolve_subject_for_context
from .marks_helpers import compute_subject_marks_summary
from ..types import SubjectContext


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
    """Build the SubjectContext for rendering the subject detail page.

    This resolves the subject using the normalized Semester/Subject schema,
    aggregates assignment and exam data, and computes summary metrics used
    by the subject template (including projected totals when a desired
    final total is provided).
    """

    # Resolve the subject for this semester/year/code
    subject = resolve_subject_for_context(session, semester=semester, year=year, code=code)
    if not subject:
        return None

    sid = getattr(subject, "id", None)
    if sid is None:
        return None

    # Fetch all assignments for this subject (normalized by subject_id)
    assignments = session.exec(
        select(Assignment)
        .where(Assignment.subject_id == sid)
        .order_by(col(Assignment.id))
    ).all()

    examinations = session.exec(
        select(Examination).where(Examination.subject_id == sid)
    ).all()
    exam_setting = session.exec(
        select(ExamSettings).where(ExamSettings.subject_id == sid)
    ).first()

    marks = compute_subject_marks_summary(
        assignments=assignments,
        examinations=examinations,
        exam_settings=exam_setting,
        exam_weight_param=exam_weight,
        final_total=final_total,
        total_mark=total_mark,
    )

    # Prerequisite relationships for this subject
    prereq_manager = SubjectPrerequisiteManager(session)
    prerequisites = prereq_manager.get_prerequisites(sid)
    required_for = prereq_manager.get_required_for(sid)

    # Start with any error propagated from the query string
    error_messages: List[str] = []
    if error_message not in (None, ""):
        error_messages.append(str(error_message))

    ctx: SubjectContext = {
        "semester": semester,
        "year": str(year),
        "subject": subject,
        "assignments": assignments,
        "examinations": examinations,
        "total_weighted": round(marks["total_weighted"], 2),
        "projected_total_weighted": marks["projected_total_weighted"],
        "total_weight_percent": round(marks["total_scoring_weight_percent"], 2) if marks["total_scoring_weight_percent"] is not None else None,
        "average": marks["average"],
        "final_total": marks["desired_goal"],
        "total_mark": marks["desired_goal"],
        "effective_exam_weight": marks["effective_exam_weight"],
        "required_exam_mark": None if marks["required_exam_mark"] is None else round(marks["required_exam_mark"], 2),
        "requirement_status": marks["requirement_status"],
        "ps_exam": marks["ps_exam"],
        "ps_factor": marks["ps_factor"] if marks["ps_exam"] else None,
        "raw_exam_percent": marks["raw_exam_percent"],
        "exam_mark": marks["raw_exam_percent"],
        "assignment_weighted_sum": round(marks["assignment_weighted_sum"], 2),
        "assignment_weight_percent": round(marks["assignment_weight_percent"], 2),
        "exam_weighted_sum": round(marks["exam_contribution"], 2),
        "effective_scoring_exam_weight": round(marks["effective_scoring_exam_weight"], 2) if marks["effective_scoring_exam_weight"] is not None else None,
        "return_to": return_to,
        "legacy_exam_mark": marks["legacy_exam_mark"],
        "legacy_exam_weight": marks["legacy_exam_weight"],
        "has_legacy_exam": marks["has_legacy_exam"],
        "has_assignment_exam": marks["has_assignment_exam"],
        "count_s": marks["count_s"],
        "count_u": marks["count_u"],
        "count_hd": marks["count_hd"],
        "count_d": marks["count_d"],
        "count_c": marks["count_c"],
        "count_p": marks["count_p"],
        "count_ps": marks["count_ps"],
        "count_f": marks["count_f"],
        # For the updated UI
        "final_exam_mark_weight": marks["effective_exam_weight"],
        "summary_exam_mark": marks["exam_contribution"],
        "error_messages": error_messages,
        "prerequisites": prerequisites,
        "required_for": required_for,
        "assignment_unweighted_sum": round(marks["assignment_unweighted_sum"], 2),
        "overall_assignment_unweighted": round(marks["overall_assignment_unweighted"], 2),
    }
    return ctx
