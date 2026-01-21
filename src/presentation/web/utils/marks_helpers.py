from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from src.infrastructure.db.models import Assignment, Examination, ExamSettings, GradeType


def compute_subject_marks_summary(
    assignments: Sequence[Assignment],
    examinations: Sequence[Examination],
    exam_settings: Optional[ExamSettings],
    exam_weight_param: Optional[float],
    final_total: Optional[str],
    total_mark: Optional[str],
) -> Dict[str, Any]:
    """Compute weighted marks, averages, and projection info for a subject.

    This is a pure helper extracted from build_subject_context. It does
    not hit the database; callers supply the relevant rows.
    """
    # Prefer a single main exam row if present
    single_exam: Optional[Examination] = None
    for ex in examinations:
        if getattr(ex, "exam_type", "main") == "main":
            single_exam = ex
            break
    if single_exam is None and examinations:
        single_exam = examinations[0]

    # Exam settings (PS hurdle etc.)
    setting = exam_settings
    ps_exam = bool(getattr(setting, "ps_exam", False)) if setting else False
    ps_factor = getattr(setting, "ps_factor", 40.0) if setting else 40.0

    # Separate assignment-based exam (if any) so we don't double-count it
    exam_assignment = next(
        (a for a in assignments if bool(getattr(a, "is_exam", False))),
        None,
    )
    normal_assignments = [a for a in assignments if not bool(getattr(a, "is_exam", False))]

    assignment_weighted_sum = 0.0
    assignment_unweighted_sum = 0.0
    assignment_weight_percent = 0.0

    # Grade band counters
    count_s = count_u = 0
    count_hd = count_d = count_c = 0
    count_p = count_ps = count_f = 0

    for a in normal_assignments:
        # Count grade bands regardless of numeric contribution
        if a.grade_type == GradeType.SATISFACTORY.value:
            count_s += 1
        elif a.grade_type == GradeType.UNSATISFACTORY.value:
            count_u += 1
        elif a.grade_type == GradeType.HIGH_DISTINCTION.value:
            count_hd += 1
        elif a.grade_type == GradeType.DISTINCTION.value:
            count_d += 1
        elif a.grade_type == GradeType.CREDIT.value:
            count_c += 1
        elif a.grade_type == GradeType.PASS.value:
            count_p += 1
        elif a.grade_type == GradeType.PASS_SUPPLEMENTARY.value:
            count_ps += 1
        elif a.grade_type == GradeType.FAIL.value:
            count_f += 1

        if a.grade_type == GradeType.NUMERIC.value:
            if a.mark_weight not in (None, ""):
                try:
                    assignment_weight_percent += float(a.mark_weight)
                except (TypeError, ValueError):
                    pass
            if a.weighted_mark not in (None, ""):
                try:
                    assignment_weighted_sum += float(a.weighted_mark)
                except (TypeError, ValueError):
                    pass
            if a.unweighted_mark not in (None, ""):
                try:
                    assignment_unweighted_sum += float(a.unweighted_mark)
                except (TypeError, ValueError):
                    pass

    # Determine exam source: assignment-based exam takes precedence over legacy exam row
    legacy_exam_mark = None
    legacy_exam_weight = None
    has_legacy_exam = False
    has_assignment_exam = False

    exam_weight_value: float = 0.0
    exam_weighted_sum: Optional[float] = None
    raw_exam_percent: Optional[float] = None

    if exam_assignment is not None:
        has_assignment_exam = True
        if exam_assignment.mark_weight not in (None, ""):
            try:
                exam_weight_value = float(exam_assignment.mark_weight)
            except (TypeError, ValueError):
                exam_weight_value = 0.0
        if exam_assignment.weighted_mark not in (None, ""):
            try:
                exam_weighted_sum = float(exam_assignment.weighted_mark)
            except (TypeError, ValueError):
                exam_weighted_sum = None
        # Prefer explicit unweighted_mark for raw percent if available
        if exam_assignment.unweighted_mark not in (None, ""):
            try:
                raw_exam_percent = float(exam_assignment.unweighted_mark)
            except (TypeError, ValueError):
                raw_exam_percent = None
    elif single_exam is not None:
        has_legacy_exam = True
        try:
            exam_weight_value = float(getattr(single_exam, "exam_weight", 0.0))
        except (TypeError, ValueError):
            exam_weight_value = 0.0
        try:
            legacy_exam_mark = float(getattr(single_exam, "exam_mark", 0.0))
        except (TypeError, ValueError):
            legacy_exam_mark = None
        legacy_exam_weight = exam_weight_value if exam_weight_value else None
        # With the new model, exam_mark is stored as a weighted contribution
        exam_weighted_sum = legacy_exam_mark
        if legacy_exam_mark is not None and exam_weight_value > 0:
            raw_exam_percent = (legacy_exam_mark / exam_weight_value) * 100.0

    # If the caller supplied an explicit exam_weight for projections and there is
    # no stored exam yet, prefer that over an inferred weight
    inferred_remaining = 0.0
    if not has_legacy_exam and not has_assignment_exam:
        inferred_remaining = max(0.0, 100.0 - assignment_weight_percent)

    # Effective exam weight used for projections
    effective_exam_weight = exam_weight_value or (
        exam_weight_param if (exam_weight_param is not None and not has_legacy_exam and not has_assignment_exam) else inferred_remaining
    )

    # PS exams are treated as a hurdle in the new model; the factor is
    # displayed but does not change the weight used for scoring.
    effective_scoring_exam_weight = effective_exam_weight

    # Compute exam contribution based on the raw percent and effective weight
    exam_contribution = 0.0
    if raw_exam_percent is not None and effective_scoring_exam_weight > 0:
        exam_contribution = (raw_exam_percent / 100.0) * effective_scoring_exam_weight
    elif exam_weighted_sum is not None:
        # Fallback: treat stored exam_mark as the contribution directly
        exam_contribution = float(exam_weighted_sum)

    total_weighted = assignment_weighted_sum + exam_contribution
    total_scoring_weight_percent = assignment_weight_percent + effective_scoring_exam_weight
    average: Optional[float] = (
        round(total_weighted / total_scoring_weight_percent * 100.0, 2)
        if total_scoring_weight_percent > 0
        else None
    )

    # Compute projected requirement to hit a desired overall goal if provided
    requirement_status: Optional[str] = None
    required_exam_mark: Optional[float] = None
    projected_total_weighted: Optional[float] = None

    desired_goal: Optional[str] = None
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
                # If we already exceed the goal with current marks, mark as achieved
                if average is not None and raw_exam_percent is not None and average >= goal:
                    requirement_status = "achieved"
                    projected_total_weighted = round(total_weighted, 2)
                else:
                    effective_exam_score = effective_scoring_exam_weight
                    if effective_exam_score <= 0:
                        requirement_status = "impossible"
                    else:
                        # Solve for the required raw exam percentage R as described in docs
                        required_exam_mark = (
                            (goal / 100.0) * (assignment_weight_percent + effective_exam_score)
                            - assignment_weighted_sum
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

    return {
        "assignment_weighted_sum": assignment_weighted_sum,
        "assignment_unweighted_sum": assignment_unweighted_sum,
        "assignment_weight_percent": assignment_weight_percent,
        "count_s": count_s,
        "count_u": count_u,
        "count_hd": count_hd,
        "count_d": count_d,
        "count_c": count_c,
        "count_p": count_p,
        "count_ps": count_ps,
        "count_f": count_f,
        "legacy_exam_mark": legacy_exam_mark,
        "legacy_exam_weight": legacy_exam_weight,
        "has_legacy_exam": has_legacy_exam,
        "has_assignment_exam": has_assignment_exam,
        "exam_weight_value": exam_weight_value,
        "exam_weighted_sum": exam_weighted_sum,
        "raw_exam_percent": raw_exam_percent,
        "effective_exam_weight": effective_exam_weight,
        "effective_scoring_exam_weight": effective_scoring_exam_weight,
        "exam_contribution": exam_contribution,
        "total_weighted": total_weighted,
        "total_scoring_weight_percent": total_scoring_weight_percent,
        "average": average,
        "requirement_status": requirement_status,
        "required_exam_mark": required_exam_mark,
        "projected_total_weighted": projected_total_weighted,
        "desired_goal": desired_goal,
        "ps_exam": ps_exam,
        "ps_factor": ps_factor,
    }
