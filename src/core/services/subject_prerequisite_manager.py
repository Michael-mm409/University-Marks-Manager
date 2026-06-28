"""Service layer for managing subject prerequisites."""
from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlmodel import col
from src.infrastructure.db.models import SubjectPrerequisite, Subject

class SubjectPrerequisiteManager:
    def __init__(self, session: Session):
        self.session = session

    def add_prerequisite(
        self,
        subject_id: int,
        prerequisite_subject_id: int | None = None,
        *,
        custom_text: str | None = None,
        is_corequisite: bool = False,
    ) -> SubjectPrerequisite:
        """Add a prerequisite (or corequisite) to a subject, deduplicating if it already exists.

        Exactly one of ``prerequisite_subject_id`` or ``custom_text`` must be supplied.
        If the matching record already exists it is returned without creating a duplicate.

        Args:
            subject_id: Primary key of the subject that has this requirement.
            prerequisite_subject_id: Primary key of the subject that must be completed
                beforehand. Mutually exclusive with ``custom_text``.
            custom_text: Free-form text describing an unlinked prerequisite (e.g.
                "Completion of Year 12 Mathematics"). Mutually exclusive with
                ``prerequisite_subject_id``.
            is_corequisite: When ``True`` the relationship is treated as a corequisite
                (must be taken concurrently) rather than a prerequisite. Defaults to
                ``False``.

        Returns:
            The newly created :class:`SubjectPrerequisite` row, or the pre-existing one
            if an identical record was already present in the database.

        Raises:
            ValueError: If neither ``prerequisite_subject_id`` nor a non-blank
                ``custom_text`` is provided.
        """
        if prerequisite_subject_id is None and (not custom_text or not custom_text.strip()):
            raise ValueError("Either prerequisite_subject_id or custom_text must be provided")

        query = select(SubjectPrerequisite).where(
            col(SubjectPrerequisite.subject_id) == subject_id,
            col(SubjectPrerequisite.is_corequisite) == is_corequisite,
        )
        if prerequisite_subject_id is not None:
            query = query.where(
                col(SubjectPrerequisite.prerequisite_subject_id) == prerequisite_subject_id
            )
        else:
            query = query.where(col(SubjectPrerequisite.custom_text) == custom_text)

        existing = self.session.execute(query).scalars().first()
        if existing:
            return existing

        prereq = SubjectPrerequisite(
            subject_id=subject_id,
            prerequisite_subject_id=prerequisite_subject_id,
            custom_text=custom_text,
            is_corequisite=is_corequisite,
        )
        self.session.add(prereq)
        self.session.commit()
        self.session.refresh(prereq)
        return prereq

    def remove_prerequisite(self, subject_id: int, prerequisite_subject_id: int, is_corequisite: bool = False) -> bool:
        prereq = self.session.execute(
            select(SubjectPrerequisite).where(
                col(SubjectPrerequisite.subject_id) == subject_id,
                col(SubjectPrerequisite.prerequisite_subject_id) == prerequisite_subject_id,
                col(SubjectPrerequisite.is_corequisite) == is_corequisite,
            )
        ).scalars().first()
        if prereq:
            self.session.delete(prereq)
            self.session.commit()
            return True
        return False

    def get_prerequisites(self, subject_id: int) -> list[SubjectPrerequisite]:
        prereqs = self.session.execute(
            select(SubjectPrerequisite).where(
                col(SubjectPrerequisite.subject_id) == subject_id
            )
        ).scalars().all()
        return list(prereqs)

    def get_required_for(self, prerequisite_subject_id: int) -> list[SubjectPrerequisite]:
        subjects = self.session.execute(
            select(SubjectPrerequisite).where(
                col(SubjectPrerequisite.prerequisite_subject_id) == prerequisite_subject_id
            )
        ).scalars().all()
        return list(subjects)
