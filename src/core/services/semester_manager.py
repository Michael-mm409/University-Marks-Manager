"""Service layer for managing semesters."""
from __future__ import annotations

from typing import cast
from sqlmodel import Session, select, asc, Table

from src.infrastructure.db.models import Semester


class SemesterManager:
    """Manages business logic for semesters."""

    def __init__(self, session: Session):
        """Initialize the SemesterManager with a database session."""
        self.session = session

    def get_all_semesters(self) -> list[Semester]:
        """Retrieve all semesters from the database, sorted by year (asc), then name (asc)."""
        statement = select(Semester).order_by(asc(Semester.year), asc(Semester.name))
        results = self.session.exec(statement).all()
        return list(results)

    def get_distinct_years(self) -> list[int]:
        """Return all distinct semester years sorted ascending (smallest → biggest)."""
        # Use the model's Table column to satisfy static type checkers
        semesters_table = cast(Table, getattr(Semester, "__table__"))
        stmt = select(Semester.year).distinct().order_by(semesters_table.c.year.asc())
        years = [row for row in self.session.exec(stmt).all()]
        # Ensure ints
        return [int(y) for y in years]

    def get_semesters_for_course(self, course_id: int) -> list[Semester]:
        """Retrieve semesters assigned to a specific course, sorted by year (asc), then name (asc)."""
        stmt = (
            select(Semester)
            .where(Semester.course_id == course_id)
            .order_by(asc(Semester.year), asc(Semester.name))
        )
        return list(self.session.exec(stmt).all())

    def get_distinct_years_for_course(self, course_id: int) -> list[int]:
        """Return distinct years for semesters assigned to a specific course, sorted ascending."""
        semesters_table = cast(Table, getattr(Semester, "__table__"))
        stmt = (
            select(Semester.year)
            .where(Semester.course_id == course_id)
            .distinct()
            .order_by(asc(semesters_table.c.year))
        )
        years = [row for row in self.session.exec(stmt).all()]
        return [int(y) for y in years]
