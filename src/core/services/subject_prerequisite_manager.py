"""Service layer for managing subject prerequisites."""
from __future__ import annotations
from sqlmodel import Session, select
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
        """Add a prerequisite, either linked to a subject or as custom text.

        Exactly one of prerequisite_subject_id or custom_text should be provided.
        """
        if prerequisite_subject_id is None and (not custom_text or not custom_text.strip()):
            raise ValueError("Either prerequisite_subject_id or custom_text must be provided")

        query = select(SubjectPrerequisite).where(
            SubjectPrerequisite.subject_id == subject_id,
            SubjectPrerequisite.is_corequisite == is_corequisite,
        )
        if prerequisite_subject_id is not None:
            query = query.where(
                SubjectPrerequisite.prerequisite_subject_id == prerequisite_subject_id
            )
        else:
            query = query.where(SubjectPrerequisite.custom_text == custom_text)

        existing = self.session.exec(query).first()
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
        prereq = self.session.exec(
            select(SubjectPrerequisite).where(
                SubjectPrerequisite.subject_id == subject_id,
                SubjectPrerequisite.prerequisite_subject_id == prerequisite_subject_id,
                SubjectPrerequisite.is_corequisite == is_corequisite
            )
        ).first()
        if prereq:
            self.session.delete(prereq)
            self.session.commit()
            return True
        return False

    def get_prerequisites(self, subject_id: int) -> list[SubjectPrerequisite]:
        prereqs = self.session.exec(
            select(SubjectPrerequisite).where(
                SubjectPrerequisite.subject_id == subject_id
            )
        ).all()
        return list(prereqs)

    def get_required_for(self, prerequisite_subject_id: int) -> list[SubjectPrerequisite]:
        subjects = self.session.exec(
            select(SubjectPrerequisite).where(
                SubjectPrerequisite.prerequisite_subject_id == prerequisite_subject_id
            )
        ).all()
        return list(subjects)
