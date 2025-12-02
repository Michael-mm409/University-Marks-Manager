"""Service layer for managing courses."""
from __future__ import annotations

from typing import Optional, Iterable

from sqlmodel import Session, select
from sqlalchemy import func

from src.infrastructure.db.models import Course, Subject, Semester


class CourseManager:
    """Manages business logic for courses."""

    def __init__(self, session: Session):
        """Initialize the CourseManager with a database session."""
        self.session = session

    def create_course(self, name: str, code: str) -> Course:
        """Create a new course.

        Args:
            name: The name of the course.
            code: The optional course code.

        Returns:
            The newly created Course object.
        """
        # Normalize inputs: trim whitespace; keep code case as-is but trimmed
        name = name.strip()
        code = code.strip()
        course = Course(name=name, code=code)
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def get_all_courses(self) -> list[Course]:
        """Retrieve all courses from the database.

        Returns:
            A list of all Course objects.
        """
        statement = select(Course)
        results = self.session.exec(statement).all()
        return list(results)

    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """Get a course by its ID, loading related subjects and semester."""
        statement = select(Course).where(Course.id == course_id)
        course = self.session.exec(statement).first()
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
        return self.session.exec(statement).first()

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

        semesters = self.session.exec(select(Semester).where(Semester.year == year)).all()
        for sem in semesters:
            self._link_semester_and_subjects(course, sem)
        return self.get_course_by_id(course_id)

    def assign_all_semesters_to_course(self, course_id: int) -> Optional[Course]:
        """Assign all existing semesters to a course and auto-link their subjects."""
        course = self.get_course_by_id(course_id)
        if not course:
            return None
        semesters = self.session.exec(select(Semester)).all()
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
        semesters = self.session.exec(
            select(Semester).where(Semester.year == year, Semester.course_id == course_id)
        ).all()
        for sem in semesters:
            self.unassign_semester_from_course(course_id, sem.id)  # type: ignore[arg-type]
        return self.get_course_by_id(course_id)

    def get_unassigned_semesters(self) -> list[Semester]:
        """Return semesters that are not assigned to any course."""
        return list(self.session.exec(select(Semester).where(Semester.course_id == None)).all())

    def get_unassigned_years(self) -> list[int]:
        """Return years that have at least one unassigned semester (descending)."""
        years = self.session.exec(
            select(Semester.year).where(Semester.course_id == None).distinct()
        ).all()
        return sorted([int(y) for y in years], reverse=True)

    # New: update and delete
    def update_course(self, course_id: int, name: str, code: str) -> Optional[Course]:
        """Update an existing course's name and code (trimmed)."""
        course = self.get_course_by_id(course_id)
        if not course:
            return None
        course.name = name.strip()
        course.code = code.strip()
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
