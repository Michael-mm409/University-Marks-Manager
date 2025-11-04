"""Service layer for managing courses."""
from __future__ import annotations

from typing import Optional, Iterable

from sqlmodel import Session, select
from sqlalchemy import func

from src.infrastructure.db.models import Course, Subject, Semester, CourseSubjectLink


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
        """Add an existing subject to a course.

        Args:
            course_id: The ID of the course.
            subject_id: The ID of the subject to add.

        Returns:
            The updated Course object or None if not found.
        """
        course = self.get_course_by_id(course_id)
        subject = self.session.get(Subject, subject_id)

        if not course or not subject:
            return None

        # Check if the link already exists
        existing_link = self.session.exec(
            select(CourseSubjectLink).where(
                CourseSubjectLink.course_id == course_id,
                CourseSubjectLink.subject_id == subject_id,
            )
        ).first()

        if existing_link:
            return course  # Subject is already in the course

        link = CourseSubjectLink(course_id=course_id, subject_id=subject_id)
        self.session.add(link)
        self.session.commit()
        self.session.refresh(course)
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
        """Link only unassigned semesters to a course and attach subjects via link table.

        Note: We do not steal semesters from other courses; only semesters with course_id=None are linked.
        """
        # Link the semester to the course (one Course -> many Semesters)
        if semester.course_id is None:
            semester.course_id = course.id
            self.session.add(semester)
            self.session.commit()

            # Auto-link all subjects that belong to this semester/year to the course
            subjects_in_semester = self.session.exec(
                select(Subject).where(
                    Subject.semester_name == semester.name,
                    Subject.year == str(semester.year),
                )
            ).all()

            created = False
            for subj in subjects_in_semester:
                exists = self.session.exec(
                    select(CourseSubjectLink).where(
                        CourseSubjectLink.course_id == course.id,
                        CourseSubjectLink.subject_id == subj.id,
                    )
                ).first()
                if not exists:
                    self.session.add(CourseSubjectLink(course_id=course.id, subject_id=subj.id))
                    created = True
            if created:
                self.session.commit()

    def unassign_semester_from_course(self, course_id: int, semester_id: int) -> Optional[Course]:
        """Remove a semester from a course and unlink its subjects from the course."""
        course = self.get_course_by_id(course_id)
        semester = self.session.get(Semester, semester_id)
        if not course or not semester:
            return None
        if semester.course_id != course.id:
            return course

        # Unlink course from semester
        semester.course_id = None
        self.session.add(semester)
        self.session.commit()

        # Remove subject links for this semester
        subjects_in_semester = self.session.exec(
            select(Subject).where(
                Subject.semester_name == semester.name,
                Subject.year == str(semester.year),
            )
        ).all()
        removed = False
        for subj in subjects_in_semester:
            link = self.session.exec(
                select(CourseSubjectLink).where(
                    CourseSubjectLink.course_id == course.id,
                    CourseSubjectLink.subject_id == subj.id,
                )
            ).first()
            if link:
                self.session.delete(link)
                removed = True
        if removed:
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
        """Delete a course: unlink semesters and remove subject associations first.

        Returns True if deleted, False if not found.
        """
        course = self.get_course_by_id(course_id)
        if not course:
            return False
        # Unlink semesters
        semesters = self.session.exec(select(Semester).where(Semester.course_id == course_id)).all()
        for sem in semesters:
            sem.course_id = None
            self.session.add(sem)
        # Remove subject links
        links = self.session.exec(select(CourseSubjectLink).where(CourseSubjectLink.course_id == course_id)).all()
        for link in links:
            self.session.delete(link)
        self.session.commit()
        # Now delete course
        self.session.delete(course)
        self.session.commit()
        return True
