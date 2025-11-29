from sqlmodel import Session, select
from src.infrastructure.db.models import Subject, Semester, GradeScale, Course

class GradeCalculator:
    def __init__(self, session: Session):
        self.session = session

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
                GradeScale(scale_name="Standard", grade="P", label="Pass", min_mark=50.0, gpa_point=2.0),
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
        Calculate Weighted Average Mark (WAM).
        WAM = Sum(Mark * CreditPoints) / Sum(CreditPoints)
        Only includes subjects with a non-zero total_mark.
        """
        # Join Subject and Semester to filter by course if needed
        # Note: Subject.semester_id is the FK to Semester
        query = select(Subject).join(Semester, Subject.semester_id == Semester.id) # type: ignore
        
        if course_id is not None:
            query = query.where(Semester.course_id == course_id)
            
        subjects = self.session.exec(query).all()
        
        total_weighted_marks = 0.0
        total_credit_points = 0
        
        for subject in subjects:
            # Only count subjects that have a final mark
            if subject.total_mark is not None and subject.total_mark > 0:
                # Use credit_points from subject, default to 6 if missing (though model defaults to 6)
                cp = getattr(subject, "credit_points", 6)
                total_weighted_marks += subject.total_mark * cp
                total_credit_points += cp
                
        if total_credit_points == 0:
            return None
            
        return round(total_weighted_marks / total_credit_points, 2)

    def calculate_grade_counts(self, course_id: int | None = None) -> dict[str, int]:
        """
        Calculate the count of subjects in each grade band.
        Uses GradeScale from DB.
        """
        query = select(Subject).join(Semester, Subject.semester_id == Semester.id) # type: ignore
        
        if course_id is not None:
            query = query.where(Semester.course_id == course_id)
            
        subjects = self.session.exec(query).all()
        scales = self._get_grade_scales(course_id)
        
        # Initialize counts for all defined grades
        counts = {s.grade: 0 for s in scales}
        # Sort scales by min_mark descending to find the highest matching band first
        # (Already sorted by _get_grade_scales, but good to be sure if logic changes)
        
        for subject in subjects:
            if subject.total_mark is not None:
                mark = subject.total_mark
                # Consistent with WAM calculation: only count if > 0
                if mark > 0:
                    for scale in scales:
                        if mark >= scale.min_mark:
                            counts[scale.grade] += 1
                            break
                        
        return counts

    def calculate_gpa(self, course_id: int | None = None) -> float | None:
            """
            Calculate Grade Point Average (GPA).
            GPA = Sum(GradePoints * CreditPoints) / Sum(CreditPoints)
            Uses GradeScale from DB.
            """
            query = select(Subject).join(Semester, Subject.semester_id == Semester.id) # type: ignore
            
            if course_id is not None:
                query = query.where(Semester.course_id == course_id)
                
            subjects = self.session.exec(query).all()
            scales = self._get_grade_scales(course_id)
            
            total_grade_points = 0.0
            total_credit_points = 0
            
            for subject in subjects:
                if subject.total_mark is not None and subject.total_mark > 0:
                    mark = subject.total_mark
                    cp = getattr(subject, "credit_points", 6)
                    
                    gp = 0.0
                    for scale in scales:
                        if mark >= scale.min_mark:
                            gp = scale.gpa_point
                            break
                    
                    total_grade_points += gp * cp
                    total_credit_points += cp
                    
            if total_credit_points == 0:
                return None
                
            return round(total_grade_points / total_credit_points, 2)


