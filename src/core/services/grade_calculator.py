import re
from typing import Sequence, Any, cast
from sqlmodel import Session, select, func
from sqlalchemy import case
from src.infrastructure.db.models import Subject, Semester, GradeScale, Course, ExamSettings, SubjectRule, Assignment

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
        from src.infrastructure.db.models import Examination, SubjectRule, Assignment
        
        rules = self.session.exec(select(SubjectRule).where(SubjectRule.subject_id == subject.id)).all()
        all_assignments = list(getattr(subject, "assignments", []) or [])
        
        # Check dedicated examinations table
        exam_record = self.session.exec(select(Examination).where(Examination.subject_id == subject.id)).first()

        summary = []
        used_assignment_ids: set[int] = set()
        rule_patterns = []

        def _assignment_id(assignment: Assignment) -> int | None:
            return assignment.id if assignment.id is not None else None

        # 2. Process Rules (Module Reviews, etc.)
        for rule in rules:
            clean_pattern = (rule.sql_pattern or "").replace('%', '').lower()
            rule_patterns.append(clean_pattern)
            
            matches = [a for a in all_assignments if not a.is_exam and (aid := _assignment_id(a)) is not None 
                       and aid not in used_assignment_ids and clean_pattern in (a.assessment or "").lower()]
            
            matches.sort(key=lambda x: (x.unweighted_mark or 0), reverse=True)
            core_items = matches[:rule.max_count]
            
            for item in matches: # Mark all as used
                if (aid := _assignment_id(item)) is not None: used_assignment_ids.add(aid)
            
            summary.append({
                "type": "rule",
                "label": rule.rule_label,
                "count": len(core_items),
                "unweighted_avg": sum((a.unweighted_mark or 0) for a in core_items) / len(core_items) if core_items else 0,
                "total_weight": sum((a.mark_weight or 0) for a in core_items),
                "weighted_score": round(sum((a.weighted_mark or 0) for a in matches), 2),
                "bonus_count": max(0, len(matches) - rule.max_count),
                "core_items": core_items,
            })

        # 3. Process Exam (The Hybrid Check)
        exam_assignment = next((a for a in all_assignments if a.is_exam), None)
        
        # 3. Process Exam
        if exam_record or exam_assignment or getattr(subject, "has_exam", False):
            if exam_record:
                # Raw mark (e.g., 45.66) and Weight (e.g., 60.0)
                raw_mark = float(exam_record.exam_mark or 0)
                weight = float(exam_record.exam_weight or 60.0)
                
                # Logic: Calculate the actual percentage of the exam first
                # If you got 45.66 out of 60, your percentage is 76.10
                unweighted = (raw_mark / weight)  if weight > 0 else 0
                score = raw_mark # The weighted points contribute to total_mark
            elif exam_assignment:
                # Standard assignment logic
                unweighted = (exam_assignment.unweighted_mark or 0) * 100 if (exam_assignment.unweighted_mark or 0) <= 1 else (exam_assignment.unweighted_mark or 0)
                weight = (exam_assignment.mark_weight or 0)
                score = (exam_assignment.weighted_mark or 0)
            else:
                unweighted, weight, score = 0, 0, 0

            summary.append({
                "type": "exam",
                "label": "Final Examination",
                "count": 1 if (exam_record or exam_assignment) else 0,
                "unweighted_avg": round(unweighted, 2), # This will now be 76.10
                "total_weight": weight,
                "weighted_score": round(score, 2),
                "bonus_count": 0,
                "core_items": [exam_record] if exam_record else ([exam_assignment] if exam_assignment else []),
            })

        # 4. Process General Assignments
        remaining = [a for a in all_assignments if _assignment_id(a) not in used_assignment_ids 
                     and not a.is_exam and not any(p in (a.assessment or "").lower() for p in rule_patterns)]

        for a in remaining:
            summary.append({
                "type": "general", "label": a.assessment, "count": 1,
                "unweighted_avg": (a.unweighted_mark or 0), "total_weight": (a.mark_weight or 0),
                "weighted_score": round((a.weighted_mark or 0), 2), "bonus_count": 0, "core_items": [a],
            })

        # 5. Final Calculations & Grade Goals
        type_order = {"rule": 0, "general": 1, "exam": 2}
        summary.sort(key=lambda x: (type_order.get(x["type"], 99), x["label"]))

        # Check for Total Mark override (The "79")
        db_total_mark = float(getattr(subject, "total_mark", 0) or 0)
        total_achieved = db_total_mark if db_total_mark > 0 else sum(row["weighted_score"] for row in summary)
        
        # Weight synthesis for the UI
        non_exam_weight = sum(row["total_weight"] for row in summary if row["type"] != "exam")
        for row in summary:
            if row["type"] == "exam" and row["total_weight"] <= 0:
                row["total_weight"] = max(0.0, 100.0 - non_exam_weight)

        # Remaining weight logic
        if db_total_mark > 0:
            remaining_weight = 0.0
        else:
            marked_weight = sum(row["total_weight"] for row in summary if any(getattr(i, 'unweighted_mark', None) is not None for i in row["core_items"]))
            remaining_weight = max(0.0, 100.0 - marked_weight)

        grade_goals = []
        for label, target in [("Pass", 50), ("Credit", 65), ("Distinction", 75), ("High Distinction", 85)]:
            if total_achieved >= target:
                status, req_p = "Achieved", 0.0
            elif remaining_weight <= 0:
                status, req_p = "Impossible", 0.0
            else:
                req_p = ((target - total_achieved) / remaining_weight) * 100
                status = "Impossible" if req_p > 100 else f"{max(0.0, req_p):.2f}%"

            grade_goals.append({
                "label": label, "target": target, "needed": status, "status": status,
                "required_percent": round(req_p, 2), "current_weighted_score": round(total_achieved, 2),
                "remaining_weight": round(remaining_weight, 2),
            })

        return {"summaries": summary, "grade_goals": grade_goals}