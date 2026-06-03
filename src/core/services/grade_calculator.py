import math
import re
from typing import Sequence, Any, cast
from sqlmodel import Session, select, func, case
from src.infrastructure.db.models import Subject, Semester, GradeScale, Course, ExamSettings, SubjectRule, Assignment, Examination


def academic_round(val: float) -> int:
    """Round using strict half-up rules (e.g. 84.5 → 85, not banker's rounding)."""
    return math.floor(val + 0.5)


def _round2dp(val: float) -> float:
    """Half-up round to 2 decimal places. Avoids Python's banker's rounding (round())
    so that e.g. 19.125 → 19.13 instead of 19.12."""
    return math.floor(val * 100 + 0.5) / 100

WEIGHT_THRESHOLD = 40.0


def _derive_assessment_category(name: str, explicit_category: Any = None) -> str:
    if explicit_category:
        return str(explicit_category)
    derived = re.sub(r"\s*[-_:]*\s*\d+\s*$", "", name).strip()
    return derived or name or "Assessments"


def process_assessments(assessments: Sequence[Any], rules: Sequence[SubjectRule] | None = None) -> dict[str, Any]:
    standalone_assessments: list[dict[str, Any]] = []
    grouped_assessments: dict[str, dict[str, Any]] = {}

    rule_patterns: list[tuple[str, str]] = []
    for rule in rules or []:
        pattern = (getattr(rule, "sql_pattern", "") or "").replace("%", "").strip().lower()
        label = str(getattr(rule, "rule_label", "") or "").strip()
        if pattern and label:
            rule_patterns.append((pattern, label))

    def _derive_category(name: str, explicit_category: Any = None) -> str:
        lowered_name = (name or "").lower()
        for pattern, label in rule_patterns:
            if pattern in lowered_name:
                return label
        return _derive_assessment_category(name, explicit_category)

    for index, assessment in enumerate(assessments, start=1):
        name = getattr(assessment, "name", None) or getattr(assessment, "assessment", None) or f"Assessment {index}"
        weight_val = getattr(assessment, "weight", None) or getattr(assessment, "mark_weight", 0.0)
        score_val = getattr(assessment, "score", None) or getattr(assessment, "weighted_mark", None) or getattr(assessment, "unweighted_mark", None)
        
        category = _derive_category(name, getattr(assessment, "category", None))

        # Fix: Ensure types are cast safely once
        weight = float(weight_val) if weight_val is not None else 0.0
        score = float(score_val) if score_val is not None else None

        row = {
            "name": name,
            "weight": weight,
            "score": score,
            "category": category,
        }

        if weight > WEIGHT_THRESHOLD:
            standalone_assessments.append(row)
            continue

        group = grouped_assessments.setdefault(
            category,
            {"rows": [], "weight": 0.0, "score_total": 0.0, "scored_weight": 0.0},
        )
        group["rows"].append(row)
        group["weight"] += weight
        
        # Fix: Only add to totals if a score exists to avoid NoneType errors
        if score is not None:
            group["score_total"] += score
            group["scored_weight"] += weight

    for category, group in grouped_assessments.items():
        scored_weight = group.pop("scored_weight")
        score_total = group.pop("score_total")
        group["score"] = round((score_total / group["weight"]) * 100.0, 2) if group["weight"] else None
        group["rows"] = sorted(group["rows"], key=lambda row: row["name"].lower())

    standalone_assessments.sort(key=lambda row: row["name"].lower())

    return {
        "standalone_assessments": standalone_assessments,
        "grouped_assessments": dict(sorted(grouped_assessments.items(), key=lambda item: item[0].lower())),
    }

class GradeCalculator:
    def __init__(self, session: Session):
        self.session = session
    
    def _print_sql(self, query, label="SQL"):
        """Helper to print raw SQL for debugging"""
        # Uncomment below to see SQL queries during development
        # try:
        #     compiled = query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        #     print(f"[GRADE_CALCULATOR] {label}:")
        #     print(f"  {compiled}")
        # except Exception as e:
        #     print(f"[GRADE_CALCULATOR] {label}: Could not compile - {e}")
    
    def _build_base_query(self, course_id: int | None = None):
        """
        Function Description: Build base query for subjects with valid marks, optionally filtered by course.
        
        Parameters:
        - course_id (int | None): If provided, filters subjects to those in semesters of the specified course.
        
        Returns:
        - SQLModel Select query for Subject with joins and filters applied.
        """
        query = select(Subject).join(Semester)
        
        # Filter by course if provided
        if course_id is not None:
            query = query.where(Semester.course_id == course_id)
        
        # Use comma-separated conditions in .where() to avoid Pylance Optional Operand error
        query = query.where(
            Subject.total_mark != None,
            cast(Any, Subject.total_mark) > 0
        )
        
        self._print_sql(query, f"Base Query (course_id={course_id})")
        return query

    def _get_grade_scales(self, course_id: int | None = None) -> list[GradeScale]:
        """Get grade scales for the course, seeding defaults if empty. Only use band_type='both'."""
        scale_name = None
        
        # Step 1: If course_id provided, get the scale_name from the course's grading_scale_id
        if course_id:
            course = self.session.get(Course, course_id)
            if course and getattr(course, "grading_scale_id", None):
                scale_id = course.grading_scale_id
                print(f"[GRADE_CALCULATOR] Course {course_id} has grading_scale_id={scale_id}")
                
                # Get the scale row to extract scale_name
                ref_scale = self.session.get(GradeScale, scale_id)
                if ref_scale:
                    scale_name = ref_scale.scale_name
                    print(f"[GRADE_CALCULATOR] Scale ID {scale_id} maps to scale_name: {scale_name}")

        # Step 2: Query for ALL scales with the determined scale_name (or Standard as fallback)
        if scale_name:
            query = select(GradeScale).where(
                GradeScale.scale_name == scale_name,
                GradeScale.band_type == "both"
            )
            self._print_sql(query, f"Grade Scales Query (scale_name={scale_name})")
            scales = self.session.exec(query).all()
        else:
            print(f"[GRADE_CALCULATOR] No specific scale_name, querying Standard scale")
            query = select(GradeScale).where(
                GradeScale.scale_name == "Standard",
                GradeScale.band_type == "both"
            )
            self._print_sql(query, "Grade Scales Query (Standard scale)")
            scales = self.session.exec(query).all()

        print(f"[GRADE_CALCULATOR] Found {len(scales)} grade scales from query")
        for s in scales:
            print(f"  - Grade: {s.grade}, min_mark: {s.min_mark}")

        if not scales:
            # Seed defaults for Standard scale if missing
            print("[GRADE_CALCULATOR] No scales found, seeding defaults...")
            defaults = [
                GradeScale(scale_name="Standard", grade="HD", label="High Distinction", min_mark=85.0, gpa_point=4.0, band_type="both"),
                GradeScale(scale_name="Standard", grade="D", label="Distinction", min_mark=75.0, gpa_point=3.7, band_type="both"),
                GradeScale(scale_name="Standard", grade="C", label="Credit", min_mark=65.0, gpa_point=3.3, band_type="both"),
                GradeScale(scale_name="Standard", grade="P", label="Pass", min_mark=50.01, gpa_point=2.0, band_type="both"),
                GradeScale(scale_name="Standard", grade="PS", label="Pass Supplementary", min_mark=50.0, gpa_point=2.0, band_type="both"),
                GradeScale(scale_name="Standard", grade="F", label="Fail", min_mark=0.0, gpa_point=0.0, band_type="both"),
            ]
            for d in defaults:
                self.session.add(d)
            self.session.commit()
            scales = defaults

        # Sort by min_mark descending for evaluation logic
        sorted_scales = sorted(scales, key=lambda x: x.min_mark, reverse=True)
        # Debug output
        print("[GRADE_CALCULATOR] Using grade scales for GPA:")
        for s in sorted_scales:
            print(f"  Grade: {s.grade}, min_mark: {s.min_mark}, gpa_point: {s.gpa_point}, band_type: {s.band_type}")
        return sorted_scales

    def calculate_wam(self, course_id: int | None = None) -> float | None:
        """
        Calculate Weighted Average Mark (WAM) using SQL aggregation.
        WAM = Sum(Mark * CreditPoints) / Sum(CreditPoints)
        Only includes subjects with a non-zero total_mark.
        """
        base_query = self._build_base_query(course_id)
        
        # Create subquery for aggregation
        sub = base_query.subquery()

        # Use SQL aggregation for efficiency
        wam_query = select(
            func.sum(sub.c.total_mark * sub.c.credit_points).label("weighted_sum"),
            func.sum(sub.c.credit_points).label("credit_sum")
        )
        
        self._print_sql(wam_query, f"WAM Query (course_id={course_id})")
        
        result = self.session.exec(wam_query).first()
        
        print(f"[GRADE_CALCULATOR] WAM calculation for course_id={course_id}: result={result}")
        
        if result is None or result[1] is None or result[1] == 0:
            print(f"[GRADE_CALCULATOR] WAM result is None/0")
            return None
        
        weighted_sum, credit_sum = result
        wam = round(weighted_sum / credit_sum, 2) if weighted_sum is not None else None
        print(f"[GRADE_CALCULATOR] WAM = {weighted_sum} / {credit_sum} = {wam}")
        return wam

    def calculate_grade_counts(self, course_id: int | None = None) -> dict[str, int]:
        """
        Calculate the count of subjects in each grade band.
        Uses GradeScale from DB. Each subject is counted in the HIGHEST grade it qualifies for.
        Pass Supplementary (PS) is counted using the ps_exam flag from exam_settings, and must be counted before P.
        """
        scales = self._get_grade_scales(course_id)
        # Always include all standard grades in the output, even if not present in DB
        all_grades = ['HD', 'D', 'C', 'P', 'PS', 'F']
        counts = {g: 0 for g in all_grades}
        for s in scales:
            if s.grade not in counts:
                counts[s.grade] = 0

        # Fetch all valid subjects (already filtered by total_mark > 0)
        base_query = self._build_base_query(course_id)
        subjects = self.session.exec(base_query).all()

        # Pre-fetch all exam_settings for efficiency
        subject_ids: list[int] = [subj.id for subj in subjects if subj.id is not None]
        exam_settings_map = {}
        if subject_ids:
            exam_settings = self.session.exec(
                select(ExamSettings).where(ExamSettings.subject_id.in_(subject_ids))  # type: ignore[attr-defined]
            ).all()
            exam_settings_map = {es.subject_id: es for es in exam_settings}

        for subject in subjects:
            mark = subject.total_mark
            subj_exam = exam_settings_map.get(subject.id) if subject.id is not None else None
            is_ps = subj_exam.ps_exam if subj_exam else False
            
            if is_ps:
                # Count as PS regardless of mark
                counts['PS'] += 1
                continue
            # Otherwise, assign by mark, but skip PS band
            for scale in scales:
                if scale.grade == 'PS':
                    continue  # skip PS for non-ps_exam subjects
                if mark is not None and mark >= scale.min_mark:
                    counts[scale.grade] += 1
                    break
        
        return counts

    def calculate_gpa(self, course_id: int | None = None) -> float | None:
        """
        Calculate Grade Point Average (GPA) using SQL CASE expressions.
        GPA = Sum(GradePoints * CreditPoints) / Sum(CreditPoints)
        Uses GradeScale from DB.
        """
        print(f"[GRADE_CALCULATOR] Calculating GPA for course_id={course_id}")
        scales = self._get_grade_scales(course_id)
        base_query = self._build_base_query(course_id)
        
        # Define the subquery variable so it can be referenced
        grade_subquery = base_query.subquery()
        # Build CASE expression for GPA points based on grade scales
        # Use SQLAlchemy's case() for proper typing
        whens = [(grade_subquery.c.total_mark >= scale.min_mark, scale.gpa_point) for scale in scales]
        gpa_point_expr = case(*whens, else_=0.0)
        
        # Calculate weighted GPA
        gpa_query = select(
            func.sum(gpa_point_expr * grade_subquery.c.credit_points).label("gpa_weighted_sum"),
            func.sum(grade_subquery.c.credit_points).label("credit_sum")
        )
        
        self._print_sql(gpa_query, f"GPA Query (course_id={course_id})")
        
        result = self.session.exec(gpa_query).first()
        
        # Debug: Print each subject's mark, credit points, and assigned GPA point
        print("[GRADE_CALCULATOR] GPA subject breakdown (course_id={}):".format(course_id))
        subjects = self.session.exec(base_query).all()
        for subj in subjects:
            mark = subj.total_mark
            cp = subj.credit_points
            course = getattr(subj, 'semester', None)
            course_id_dbg = getattr(course, 'course_id', None) if course else None
            assigned_gpa = 0.0
            for scale in scales:
                if mark is not None and mark >= scale.min_mark:
                    assigned_gpa = scale.gpa_point
                    break
            print(f"  Subject: {subj.subject_code}, Mark: {mark}, Credit Points: {cp}, GPA Point: {assigned_gpa}, Subject Course ID: {course_id_dbg}")
        if result is None or result[1] is None or result[1] == 0:
            return None
        
        gpa_weighted_sum, credit_sum = result
        return round(gpa_weighted_sum / credit_sum, 2) if gpa_weighted_sum is not None else None


    def calculate_subject_summary(self, subject: Subject) -> dict[str, Any]:
        if not subject.id:
            return {"summaries": [], "grade_goals": []}

        # 1. Setup Data
        rules = self.session.exec(select(SubjectRule).where(SubjectRule.subject_id == subject.id)).all()
        all_assignments = list(getattr(subject, "assignments", []) or [])
        exam_record = self.session.exec(select(Examination).where(Examination.subject_id == subject.id)).first()

        summary: list[dict[str, Any]] = []
        used_assignment_ids: set[int] = set()
        rule_patterns = []

        def _item_score(item: Any) -> float | None:
            if isinstance(item, Examination):
                return float(item.exam_mark) if item.exam_mark is not None else None
            score = getattr(item, "unweighted_mark", None)
            return float(score) if score is not None else None

        def _item_weight(item: Any) -> float:
            if isinstance(item, Examination):
                return float(item.exam_weight) if item.exam_weight is not None else 0.0
            weight = getattr(item, "mark_weight", None)
            return float(weight) if weight is not None else 0.0

        def _item_weighted_score(item: Any) -> float:
            if isinstance(item, Examination):
                return float(item.exam_mark) if item.exam_mark is not None else 0.0
            weighted_mark = getattr(item, "weighted_mark", None)
            return float(weighted_mark) if weighted_mark is not None else 0.0

        # 2. Process Rules
        for rule in rules:
            clean_pattern = (rule.sql_pattern or "").replace('%', '').lower()
            rule_patterns.append(clean_pattern)
            
            matches = [a for a in all_assignments if not a.is_exam and a.id is not None 
                       and a.id not in used_assignment_ids and clean_pattern in (a.assessment or "").lower()]
            
            matches.sort(key=lambda x: (x.unweighted_mark or 0), reverse=True)
            core_items = matches[:rule.max_count]
            scored_core_items = [item for item in core_items if _item_score(item) is not None]
            scored_core_weight = sum(_item_weight(item) for item in scored_core_items)
            weighted_score = sum(_item_weighted_score(item) for item in scored_core_items)
            
            for item in matches:
                if item.id is not None: used_assignment_ids.add(item.id)
            
            summary.append({
                "type": "rule",
                "label": rule.rule_label,
                "count": len(core_items),
                "unweighted_avg": (weighted_score / scored_core_weight) if scored_core_weight > 0 else None,
                "total_weight": sum((a.mark_weight or 0) for a in core_items),
                "weighted_score": _round2dp(weighted_score),
                "bonus_count": max(0, len(matches) - rule.max_count),  # Required by template
                "display_status": "Grouped",
                "has_scored_items": bool(scored_core_items),
                "core_items": core_items,
            })

        # 3. Process Exam
        has_exam_flag = getattr(subject, "has_exam", False)
        exam_assignment = next((a for a in all_assignments if a.is_exam), None)

        score: float | None = None
        if exam_record or exam_assignment or has_exam_flag:
            if exam_record:
                e_mark = exam_record.exam_mark
                e_weight = exam_record.exam_weight
                weight = float(e_weight) if e_weight is not None else 50.0
                score = float(e_mark) if e_mark is not None else None
                unweighted = (score / weight) if (score is not None and weight > 0) else None
            elif exam_assignment:
                weight = float(exam_assignment.mark_weight or 50.0)
                score = float(exam_assignment.weighted_mark) if exam_assignment.weighted_mark is not None else None
                unweighted = (float(exam_assignment.unweighted_mark) / 100) if exam_assignment.unweighted_mark else None
            else:
                weight = 50.0
                unweighted, score = None, None

            if weight > 0:
                summary.append({
                    "type": "exam",
                    "label": "Final Examination",
                    "count": 1,
                    "unweighted_avg": unweighted,
                    "total_weight": weight,
                    "weighted_score": _round2dp(score) if score is not None else 0.0,
                    "bonus_count": 0,
                    "has_scored_items": score is not None,
                    "core_items": [exam_record] if exam_record else ([exam_assignment] if exam_assignment else []),
                })

        # 4. Process General Assignments
        remaining = [a for a in all_assignments if a.id not in used_assignment_ids 
                    and not a.is_exam and not any(p in (a.assessment or "").lower() for p in rule_patterns)]

        grouped_general: dict[str, list[Assignment]] = {}
        for a in remaining:
            a_weight = _item_weight(a)
            a_score = _item_score(a)
            if a_weight >= WEIGHT_THRESHOLD:
                summary.append({
                    "type": "general",
                    "label": a.assessment or "Assessment",
                    "count": 1,
                    "unweighted_avg": round(a_score, 4) if a_score is not None else None,
                    "total_weight": round(a_weight, 2),
                    "weighted_score": _round2dp(_item_weighted_score(a)),
                    "bonus_count": 0,  # Required by template
                    "display_status": "Standalone",
                    "has_scored_items": a_score is not None,
                    "core_items": [a],
                })
            else:
                cat = _derive_assessment_category(str(a.assessment or ""), getattr(a, "category", None))
                grouped_general.setdefault(cat, []).append(a)

        for category, items in grouped_general.items():
            scored_items = [item for item in items if _item_score(item) is not None]
            total_weight = sum(_item_weight(item) for item in items)
            weighted_score = sum(_item_weighted_score(item) for item in scored_items)
            scored_weight = sum(_item_weight(item) for item in scored_items)
            unweighted_avg = (weighted_score / scored_weight) if scored_weight > 0 else None
            
            summary.append({
                "type": "general",
                "label": category,
                "count": len(items),
                "unweighted_avg": round(unweighted_avg, 4) if unweighted_avg is not None else None,
                "total_weight": total_weight,
                "weighted_score": _round2dp(weighted_score),
                "bonus_count": 0,  # Required by template
                "display_status": "Grouped",
                "has_scored_items": bool(scored_items),
                "core_items": items,
            })

        # 5. Final Calculations & Grade Goals
        type_order = {"rule": 0, "general": 1, "exam": 2}
        summary.sort(key=lambda x: (type_order.get(x["type"], 99), x["label"]))

        # Check for Total Mark override (e.g., if a final grade is already uploaded)
        raw_total = getattr(subject, "total_mark", 0.0)
        db_total_mark = float(raw_total) if raw_total is not None else 0.0
        
        total_achieved = 0.0
        remaining_weight_value = 0.0

        if db_total_mark > 0:
            total_achieved = round(db_total_mark, 2)
            remaining_weight_value = 0.0
        else:
            # Calculate from summary items
            for row in summary:
                total_achieved += row["weighted_score"]
                
                # Logic: If the whole row has no scores, add its full weight to remaining
                if not row["has_scored_items"]:
                    remaining_weight_value += float(row["total_weight"] or 0.0)
                else:
                    # If it's a group, check for individual unscored items
                    # We use the 'core_items' list to find assignments without a mark
                    for item in row["core_items"]:
                        if _item_score(item) is None:
                            remaining_weight_value += _item_weight(item)

        remaining_weight = round(remaining_weight_value, 2)
        total_achieved = _round2dp(total_achieved)

        # Apply university half-up rounding before threshold checks so that
        # e.g. 84.61 rounds to 85 and correctly satisfies an HD (85) threshold.
        rounded_total = academic_round(total_achieved)

        grade_goals = []
        for label, target in [("Pass", 50), ("Credit", 65), ("Distinction", 75), ("High Distinction", 85)]:
            if rounded_total >= target:
                status = "Achieved"
                req_p = 0.0
            elif remaining_weight <= 0:
                status = "Impossible"
                req_p = 0.0
            else:
                needed_from_remaining = (target - total_achieved)
                req_p = (needed_from_remaining / remaining_weight) * 100

                if req_p > 100:
                    status = "Impossible"
                else:
                    status = f"{max(0.0, req_p):.2f}%"

            grade_goals.append({
                "label": label,
                "target": target,
                "status": status,
                "required_percent": round(req_p, 2)
            })

        return {
            "summaries": summary, 
            "grade_goals": grade_goals, 
            "total_achieved": total_achieved, 
            "remaining_weight": remaining_weight
        }