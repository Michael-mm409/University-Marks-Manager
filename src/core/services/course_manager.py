"""Service layer for managing courses."""
from __future__ import annotations

from typing import Any, Optional, Iterable, cast

from sqlalchemy.orm import Session
from sqlalchemy import select, func, Column
from sqlmodel import col

from src.infrastructure.db.models import Course, Subject, Semester


class CourseManager:
    """Manages business logic for courses."""

    def __init__(self, session: Session):
        """Initialize the CourseManager with a database session."""
        self.session = session

    def create_course(self, name: str, code: str, grading_scale_id: int, university_id: int | None = None, new_university_name: str | None = None) -> Course:
        """Create a new course, creating a university if needed."""
        name = name.strip()
        code = code.strip()
        if university_id is None and new_university_name:
            from src.infrastructure.db.models import University
            uni_name = new_university_name.strip()
            existing = self.session.execute(select(University).where(col(University.name) == uni_name)).scalars().first()
            if existing:
                university_id = existing.id
            else:
                new_uni = University(name=uni_name)
                self.session.add(new_uni)
                self.session.commit()
                self.session.refresh(new_uni)
                university_id = new_uni.id
        course = Course(name=name, code=code, grading_scale_id=grading_scale_id, university_id=university_id)
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def get_all_courses(self) -> list[Course]:
        """Retrieve all courses from the database, with related university and grading_scale."""
        from sqlalchemy.orm import selectinload
        statement = select(Course).options(
            selectinload(cast(Any, Course.university)),
            selectinload(cast(Any, Course.grading_scale))
        )
        results = self.session.execute(statement).scalars().all()
        return list(results)

    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """Get a course by its ID, loading related subjects and semester."""
        statement = select(Course).where(col(Course.id) == course_id)
        course = self.session.execute(statement).scalars().first()
        return course

    def get_course_by_code(self, course_code: str) -> Optional[Course]:
        """Get a course by its unique code (case-insensitive, trimmed on both sides).

        This tolerates legacy rows that may contain leading/trailing whitespace.
        """
        if course_code is None:
            return None
        normalized = str(course_code).strip()
        # Case-insensitive compare and trim DB value as well
        db_code_normalized = func.trim(func.lower(Course.code))
        statement = select(Course).where(db_code_normalized == func.lower(normalized))
        return self.session.execute(statement).scalars().first()

    # Legacy subject-link helper retained for compatibility but unused now
    def get_unlinked_subjects(self, course_id: int) -> list[Subject]:
        """
        Short description.

        Args:
            course_id: Description.

        Returns:
            Description.

        Raises:
            Description.
        """
        return []

    def add_subject_to_course(self, course_id: int, subject_id: int) -> Optional[Course]:
        """Add an existing subject to a course (deprecated - subjects belong to semesters).

        This method is deprecated as subjects are implicitly associated with courses
        through their semester relationship. Use assign_semester_to_course instead.

        Args:
            course_id: The ID of the course.
            subject_id: The ID of the subject to add.

        Returns:
            The Course object (no-op for backward compatibility).
        """
        course = self.get_course_by_id(course_id)
        return course

    def assign_semester_to_course(
        self, course_id: int, semester_id: int
    ) -> Optional[Course]:
        """Assign an existing semester to a course.

        Args:
            course_id: The ID of the course.
            semester_id: The ID of the semester to assign.

        Returns:
            The updated Course object or None if not found.
        """
        course = self.get_course_by_id(course_id)
        semester = self.session.get(Semester, semester_id)

        if not course or not semester:
            return None

        # Link the semester to the course and auto-link subjects
        self._link_semester_and_subjects(course, semester)
        return self.get_course_by_id(course_id)

    def assign_year_to_course(self, course_id: int, year: int) -> Optional[Course]:
        """Assign all semesters for a given year to a course and auto-link subjects."""
        course = self.get_course_by_id(course_id)
        if not course:
            return None

        semesters = self.session.execute(select(Semester).where(col(Semester.year) == year)).scalars().all()
        for sem in semesters:
            self._link_semester_and_subjects(course, sem)
        return self.get_course_by_id(course_id)

    def assign_all_semesters_to_course(self, course_id: int) -> Optional[Course]:
        """Assign all existing semesters to a course and auto-link their subjects."""
        course = self.get_course_by_id(course_id)
        if not course:
            return None
        semesters = self.session.execute(select(Semester)).scalars().all()
        for sem in semesters:
            self._link_semester_and_subjects(course, sem)
        return self.get_course_by_id(course_id)

    # Internal helpers
    def _link_semester_and_subjects(self, course: Course, semester: Semester) -> None:
        """Link only unassigned semesters to a course.

        Subjects are implicitly associated with the course through their semester.
        Note: We do not steal semesters from other courses; only semesters with course_id=None are linked.
        """
        # Link the semester to the course (one Course -> many Semesters)
        if semester.course_id is None:
            semester.course_id = course.id
            self.session.add(semester)
            self.session.commit()

    def unassign_semester_from_course(self, course_id: int, semester_id: int) -> Optional[Course]:
        """Remove a semester from a course (sets course_id to NULL).
        
        Semester and its subjects remain in the database but become unassigned.
        """
        course = self.get_course_by_id(course_id)
        semester = self.session.get(Semester, semester_id)
        if not course or not semester:
            return None
        if semester.course_id != course.id:
            return course

        # Unlink course from semester (semester becomes unassigned)
        semester.course_id = None
        self.session.add(semester)
        self.session.commit()
        return self.get_course_by_id(course_id)

    def unassign_year_from_course(self, course_id: int, year: int) -> Optional[Course]:
        """Remove all semesters for the given year from the course and unlink their subjects."""
        course = self.get_course_by_id(course_id)
        if not course:
            return None
        semesters = self.session.execute(
            select(Semester).where(col(Semester.year) == year, col(Semester.course_id) == course_id)
        ).scalars().all()
        for sem in semesters:
            self.unassign_semester_from_course(course_id, sem.id)  # type: ignore[arg-type]
        return self.get_course_by_id(course_id)

    def get_unassigned_semesters(self) -> list[Semester]:
        """Return semesters that are not assigned to any course."""
        return list(self.session.execute(select(Semester).where(col(Semester.course_id).is_(None))).scalars().all())

    def get_unassigned_years(self) -> list[int]:
        """Return years that have at least one unassigned semester (descending)."""
        years = self.session.execute(
            select(col(Semester.year)).where(col(Semester.course_id).is_(None)).distinct()
        ).scalars().all()
        return sorted([int(y) for y in years], reverse=True)

    # New: update and delete
    def update_course(self, course_id: int, name: str, code: str, university_id: int | None = None, new_university_name: str | None = None) -> Optional[Course]:
        """Update an existing course's name, code, and university. Create university if needed."""
        course = self.get_course_by_id(course_id)
        if not course:
            return None
        course.name = name.strip()
        course.code = code.strip()
        # University logic
        if new_university_name and (university_id is None or university_id == "add_new"):
            from src.infrastructure.db.models import University
            uni_name = new_university_name.strip()
            existing = self.session.execute(select(University).where(col(University.name) == uni_name)).scalars().first()
            if existing:
                course.university_id = existing.id
            else:
                new_uni = University(name=uni_name)
                self.session.add(new_uni)
                self.session.commit()
                self.session.refresh(new_uni)
                course.university_id = new_uni.id
        elif university_id:
            course.university_id = university_id
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def update_gpa_scale(self, course_id: int, gpa_scale: int) -> Optional[Course]:
        """Set gpa_scale on a course and sync grading_scale_id to the matching GradeScale rows.

        The scale whose max gpa_point equals gpa_scale is resolved dynamically from
        the database, so any scale added via /settings/grade-scales/add is picked up
        automatically without code changes.
        """
        from src.infrastructure.db.models import GradeScale
        course = self.get_course_by_id(course_id)
        if not course:
            return None

        # Find which scale_name has max(gpa_point) == gpa_scale among band_type="both" rows
        all_scale_maxes = self.session.execute(
            select(col(GradeScale.scale_name), func.max(col(GradeScale.gpa_point)))
            .where(col(GradeScale.band_type) == "both")
            .group_by(col(GradeScale.scale_name))
        ).all()
        scale_name: str | None = None
        for row in all_scale_maxes:
            row_name, row_max = row[0], row[1]
            if row_max is not None and int(row_max) == gpa_scale:
                scale_name = str(row_name)
                break

        if scale_name:
            ref = self.session.execute(
                select(GradeScale).where(
                    col(GradeScale.scale_name) == scale_name,
                    col(GradeScale.band_type) == "both",
                )
            ).scalars().first()
            if ref is not None and ref.id is not None:
                course.grading_scale_id = ref.id

        course.gpa_scale = gpa_scale
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def delete_course(self, course_id: int) -> bool:
        """Delete a course and all associated semesters, subjects, assignments, and exams.

        Relies on database ON DELETE CASCADE to automatically remove all dependent records.
        Returns True if deleted, False if not found.
        """
        course = self.get_course_by_id(course_id)
        if not course:
            return False
        # Database CASCADE handles deletion of semesters and all their children
        self.session.delete(course)
        self.session.commit()
        return True

    def get_subjects_by_year(self, year: int) -> list[Subject]:
        """Retrieve all subjects for a given year.

        Args:
            year: The year for which to retrieve subjects.

        Returns:
            A list of Subject objects for the specified year.
        """
        # Now filter by Semester.year via join
        return list(
            self.session.execute(
                select(Subject)
                .join(Semester)
                .where(col(Semester.year) == int(year))
            ).scalars().all()
        )
