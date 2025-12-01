import argparse
import math
from typing import Optional

from sqlmodel import Session, select

from src.infrastructure.db.engine import get_engine
from src.infrastructure.db.models import Assignment, Examination, ExamSettings, GradeType, Subject


def compute_effective_weights(session: Session, subject_id: int) -> tuple[float, float, float]:
    """Return (assess_weight_sum, exam_weight, effective_scoring_exam_weight).

    - assess_weight_sum: sum of non-exam numeric assignment weights
    - exam_weight: existing exam.exam_weight if present or remaining (100 - assess_weight_sum)
    - effective_scoring_exam_weight: exam_weight scaled by PS factor if PS exam is enabled
    """
    assignments = session.exec(select(Assignment).where(Assignment.subject_id == subject_id)).all()
    assess_weight_sum = 0.0
    exam_assignment = next((a for a in assignments if getattr(a, "is_exam", False)), None)
    for a in assignments:
        if getattr(a, "is_exam", False):
            continue
        if a.grade_type == GradeType.NUMERIC.value and a.mark_weight is not None:
            try:
                assess_weight_sum += float(a.mark_weight)
            except Exception:
                pass
    exam = session.exec(select(Examination).where(Examination.subject_id == subject_id)).first()
    exam_weight = float(exam.exam_weight) if (exam and exam.exam_weight is not None) else max(0.0, 100.0 - assess_weight_sum)

    setting = session.exec(select(ExamSettings).where(ExamSettings.subject_id == subject_id)).first()
    ps_exam = bool(getattr(setting, "ps_exam", False)) if setting else False
    ps_factor = float(getattr(setting, "ps_factor", 40.0)) if setting else 40.0
    scaling = (ps_factor / 100.0) if ps_exam else 1.0
    effective_scoring_exam_weight = exam_weight * scaling
    return assess_weight_sum, exam_weight, effective_scoring_exam_weight


def decide_raw_or_weighted(
    assess_weight_sum: float,
    effective_scoring_exam_weight: float,
    stored_exam_mark: float,
    subject_total_mark: Optional[float],
) -> tuple[str, float]:
    """Decide whether stored value is RAW percent or WEIGHTED contribution.

    Returns a tuple of (chosen_kind, weighted_contribution).
    chosen_kind = 'raw', 'weighted', or 'ambiguous'.
    weighted_contribution is the contribution to add to weighted sums (regardless of chosen_kind).
    """
    # Guard: negative or NaN -> treat as ambiguous
    try:
        val = float(stored_exam_mark)
    except Exception:
        return ("ambiguous", 0.0)
    if math.isnan(val) or val < 0:
        return ("ambiguous", 0.0)

    # Candidate 1: interpret as RAW percent (0..100)
    contrib_from_raw = (max(0.0, min(100.0, val)) / 100.0) * max(0.0, effective_scoring_exam_weight)
    # Candidate 2: interpret as already WEIGHTED contribution
    contrib_weighted = val

    # Quick confidence rule: weighted cannot exceed effective scoring weight
    if contrib_weighted - effective_scoring_exam_weight > 1e-6:
        return ("raw", contrib_from_raw)

    # If we have a stored total_mark for the subject, pick the interpretation that is closer
    if subject_total_mark is not None and effective_scoring_exam_weight > 0:
        try:
            goal = float(subject_total_mark)
            if goal <= 0 or goal > 100:
                raise ValueError
            avg_raw = (assess_weight_sum + contrib_from_raw) / (assess_weight_sum + effective_scoring_exam_weight) * 100.0
            avg_weighted = (assess_weight_sum + contrib_weighted) / (assess_weight_sum + effective_scoring_exam_weight) * 100.0
            if abs(avg_raw - goal) + 1e-6 < abs(avg_weighted - goal) - 1e-6:
                return ("raw", contrib_from_raw)
            elif abs(avg_weighted - goal) + 1e-6 < abs(avg_raw - goal) - 1e-6:
                return ("weighted", contrib_weighted)
            # Too close to call
            return ("ambiguous", contrib_weighted)
        except Exception:
            pass

    # Without a goal, leave ambiguous cases unchanged
    return ("ambiguous", contrib_weighted)


def migrate(dry_run: bool, year: Optional[int], semester: Optional[str], subject_code: Optional[str]) -> int:
    engine = get_engine()
    total_updated = 0
    with Session(engine) as session:
        q = select(Subject)
        if year is not None:
            q = q.where(Subject.year == str(year))
        if semester is not None:
            q = q.where(Subject.semester_name == semester)
        if subject_code is not None:
            q = q.where(Subject.subject_code == subject_code)
        subjects = session.exec(q).all()
        for sub in subjects:
            sid = getattr(sub, "id", None)
            if sid is None:
                continue
            exam = session.exec(select(Examination).where(Examination.subject_id == sid)).first()
            if not exam:
                continue
            # Skip if an assignment-based exam exists; that is authoritative
            exam_assignment = session.exec(select(Assignment).where(Assignment.subject_id == sid, Assignment.is_exam == True)).first()  # noqa: E712
            if exam_assignment:
                continue

            assess_sum, exam_weight, effective_scoring_exam_weight = compute_effective_weights(session, sid)
            kind, weighted = decide_raw_or_weighted(assess_sum, effective_scoring_exam_weight, float(exam.exam_mark or 0.0), sub.total_mark)

            # If we confidently detected RAW, convert to weighted
            if kind == "raw":
                old = float(exam.exam_mark or 0.0)
                if not dry_run:
                    exam.exam_mark = round(weighted, 4)
                    session.add(exam)
                print(f"[MIGRATE] {sub.subject_code} {sub.semester_name} {sub.year}: RAW {old} -> WEIGHTED {round(weighted,4)} (eff_weight={effective_scoring_exam_weight})")
                total_updated += 1
            elif kind == "weighted":
                # Already weighted; nothing to do
                pass
            else:
                print(f"[SKIP] {sub.subject_code} {sub.semester_name} {sub.year}: ambiguous value {exam.exam_mark}; no change.")
        if not dry_run and total_updated:
            session.commit()
    return total_updated


def main():
    p = argparse.ArgumentParser(description="Normalize Examination.exam_mark to store WEIGHTED contribution.")
    p.add_argument("--apply", action="store_true", help="Apply changes (omit for dry-run)")
    p.add_argument("--year", type=int, default=None, help="Limit to a specific year")
    p.add_argument("--semester", type=str, default=None, help="Limit to a semester name (e.g., Autumn)")
    p.add_argument("--subject", type=str, default=None, help="Limit to a subject code (e.g., CSCI316)")
    args = p.parse_args()
    updated = migrate(dry_run=not args.apply, year=args.year, semester=args.semester, subject_code=args.subject)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] Updated {updated} examination rows.")


if __name__ == "__main__":
    main()
