from typing import Sequence, Any, cast
from sqlmodel import Session, select, func, col
from sqlalchemy import case
from src.infrastructure.db.models import Subject, Semester, GradeScale, Course

class GradeCalculator:
    def __init__(self, session: Session):
        self.session = session
    
    def _build_base_query(self, course_id: int | None = None):
        """Build base query for subjects with valid marks, optionally filtered by course."""
        query = (
            select(Subject)
            .join(Semester, col(Semester.id) == col(Subject.semester_id))
            .where(col(Subject.total_mark).is_not(None))
            .where(col(Subject.total_mark) > 0)
        )
        
        if course_id is not None:
            query = query.where(col(Semester.course_id) == course_id)
        
        return query

    def _get_grade_scales(self, course_id: int | None = None) -> list[GradeScale]:
        """Get grade scales for the course, seeding defaults if empty."""
        scale_id = None
        if course_id:
            course = self.session.get(Course, course_id)
            if course and getattr(course, "grading_scale_id", None):
                scale_id = course.grading_scale_id

        if scale_id:
            scales = self.session.exec(select(GradeScale).where(GradeScale.id == scale_id)).all()
        else:
            scales = self.session.exec(select(GradeScale).where(GradeScale.scale_name == "Standard")).all()

        if not scales:
            # Seed defaults for Standard scale if missing
            defaults = [
                GradeScale(scale_name="Standard", grade="HD", label="High Distinction", min_mark=85.0, gpa_point=4.0),
                GradeScale(scale_name="Standard", grade="D", label="Distinction", min_mark=75.0, gpa_point=3.7),
                GradeScale(scale_name="Standard", grade="C", label="Credit", min_mark=65.0, gpa_point=3.3),
                GradeScale(scale_name="Standard", grade="P", label="Pass", min_mark=50.01, gpa_point=2.0),
                GradeScale(scale_name="Standard", grade="PS", label="Pass Supplementary", min_mark=50.0, gpa_point=2.0),
                GradeScale(scale_name="Standard", grade="F", label="Fail", min_mark=0.0, gpa_point=0.0),
            ]
            for d in defaults:
                self.session.add(d)
            self.session.commit()
            scales = defaults

        # Sort by min_mark descending for evaluation logic
        return sorted(scales, key=lambda x: x.min_mark, reverse=True)

    def calculate_wam(self, course_id: int | None = None) -> float | None:
        """
        Calculate Weighted Average Mark (WAM) using SQL aggregation.
        WAM = Sum(Mark * CreditPoints) / Sum(CreditPoints)
        Only includes subjects with a non-zero total_mark.
        """
        base_query = self._build_base_query(course_id)
        
        # Define the subquery variable so it can be referenced
        sub = base_query.subquery()

        # Use SQL aggregation for efficiency
        result = self.session.exec(
            select(
                func.sum(sub.c.total_mark * sub.c.credit_points).label("weighted_sum"),
                func.sum(sub.c.credit_points).label("credit_sum")
            )
        ).first()
        
        if result is None or result[1] is None or result[1] == 0:
            return None
        
        weighted_sum, credit_sum = result
        return round(weighted_sum / credit_sum, 2) if weighted_sum is not None else None

    def calculate_grade_counts(self, course_id: int | None = None) -> dict[str, int]:
        """
        Calculate the count of subjects in each grade band.
        Uses GradeScale from DB. Each subject is counted in the HIGHEST grade it qualifies for.
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
        # ...existing code...
        
        # For each subject, find the highest grade it qualifies for
        # Scales are already sorted descending by min_mark
        for subject in subjects:
            mark = subject.total_mark
            if mark is not None:
                for scale in scales:
                    if mark >= scale.min_mark:
                        # ...existing code...
                        counts[scale.grade] += 1
                        break  # Count in highest matching grade only
        
        return counts

    def calculate_gpa(self, course_id: int | None = None) -> float | None:
        """
        Calculate Grade Point Average (GPA) using SQL CASE expressions.
        GPA = Sum(GradePoints * CreditPoints) / Sum(CreditPoints)
        Uses GradeScale from DB.
        """
        scales = self._get_grade_scales(course_id)
        base_query = self._build_base_query(course_id)
        
        # Define the subquery variable so it can be referenced
        grade_subquery = base_query.subquery()
        # Build CASE expression for GPA points based on grade scales
        # Use SQLAlchemy's case() for proper typing
        whens = [(grade_subquery.c.total_mark >= scale.min_mark, scale.gpa_point) for scale in scales]
        gpa_point_expr = case(*whens, else_=0.0)
        
        # Calculate weighted GPA
        result = self.session.exec(
            select(
                func.sum(gpa_point_expr * grade_subquery.c.credit_points).label("gpa_weighted_sum"),
                func.sum(grade_subquery.c.credit_points).label("credit_sum")
            )
        ).first()
        
        if result is None or result[1] is None or result[1] == 0:
            return None
        
        gpa_weighted_sum, credit_sum = result
        return round(gpa_weighted_sum / credit_sum, 2) if gpa_weighted_sum is not None else None


