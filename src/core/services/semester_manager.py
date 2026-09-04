"""Service layer for managing semesters."""
from __future__ import annotations

from sqlalchemy import select, asc
from sqlalchemy.orm import Session
from sqlmodel import col

from src.infrastructure.db.models import Semester


class SemesterManager:
    """Manages business logic for semesters."""

    def __init__(self, session: Session):
        """Initialize the SemesterManager with a database session."""
        self.session = session

    def get_all_semesters(self) -> list[Semester]:
        """Retrieve all semesters from the database, sorted by year (asc), then name (asc)."""
        statement = select(Semester).order_by(asc(col(Semester.year)), asc(col(Semester.name)))
        return list(self.session.execute(statement).scalars().all())

    def get_distinct_years(self) -> list[int]:
        """Return all distinct semester years sorted ascending (smallest → biggest)."""
        stmt = select(col(Semester.year)).distinct().order_by(asc(col(Semester.year)))
        return [int(y) for y in self.session.execute(stmt).scalars().all()]

    def get_semesters_for_course(self, course_id: int) -> list[Semester]:
        """Retrieve semesters assigned to a specific course, sorted by year (asc), then name (asc)."""
        stmt = (
            select(Semester)
            .where(col(Semester.course_id) == course_id)
            .order_by(asc(col(Semester.year)), asc(col(Semester.name)))
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_distinct_years_for_course(self, course_id: int) -> list[int]:
        """Return distinct years for semesters assigned to a specific course, sorted ascending."""
        stmt = (
            select(col(Semester.year))
            .where(col(Semester.course_id) == course_id)
            .distinct()
            .order_by(asc(col(Semester.year)))
        )
        return [int(y) for y in self.session.execute(stmt).scalars().all()]
