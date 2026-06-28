"""Service layer for managing subjects."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.db.models import Subject


class SubjectManager:
    """Manages business logic for subjects."""

    def __init__(self, session: Session):
        """Initialize the SubjectManager with a database session."""
        self.session = session

    def get_all_subjects(self) -> list[Subject]:
        """Retrieve all subjects from the database.

        Returns:
            A list of all Subject objects.
        """
        statement = select(Subject)
        results = self.session.execute(statement).scalars().all()
        return list(results)
