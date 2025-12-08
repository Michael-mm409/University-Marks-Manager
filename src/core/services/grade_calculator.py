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
        scale_name = "Standard"
        if course_id:
            course = self.session.get(Course, course_id)
            if course and course.grading_scale:
                scale_name = course.grading_scale

        scales = self.session.exec(select(GradeScale).where(GradeScale.scale_name == scale_name)).all()
        
        if not scales and scale_name == "Standard":
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
        
        # Use SQL aggregation for efficiency
        result = self.session.exec(
            select(
                func.sum(col(Subject.total_mark) * col(Subject.credit_points)).label("weighted_sum"),
                func.sum(col(Subject.credit_points)).label("credit_sum")
            )
            .select_from(base_query.subquery())
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
        counts = {s.grade: 0 for s in scales}
        
        # Fetch all valid subjects (already filtered by total_mark > 0)
        base_query = self._build_base_query(course_id)
        subjects = self.session.exec(base_query).all()
        
        # For each subject, find the highest grade it qualifies for
        # Scales are already sorted descending by min_mark
        for subject in subjects:
            mark = subject.total_mark
            if mark is not None:
                for scale in scales:
                    if mark >= scale.min_mark:
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
        
        # Build CASE expression for GPA points based on grade scales
        # Use SQLAlchemy's case() for proper typing
        whens = [(col(Subject.total_mark) >= scale.min_mark, scale.gpa_point) for scale in scales]
        gpa_point_expr = case(*whens, else_=0.0)
        
        # Calculate weighted GPA
        result = self.session.exec(
            select(
                func.sum(gpa_point_expr * col(Subject.credit_points)).label("gpa_weighted_sum"),
                func.sum(col(Subject.credit_points)).label("credit_sum")
            )
            .select_from(base_query.subquery())
        ).first()
        
        if result is None or result[1] is None or result[1] == 0:
            return None
        
        gpa_weighted_sum, credit_sum = result
        return round(gpa_weighted_sum / credit_sum, 2) if gpa_weighted_sum is not None else None


