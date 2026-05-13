from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select

from src.core.services.subject_prerequisite_manager import SubjectPrerequisiteManager
from src.infrastructure.db.models import Semester, Subject


def create_subject_core(
    session: Session,
    semester: str,
    year: str,
    subject_code: str,
    subject_name: str,
    credit_points: int,
    has_exam: bool,
    sync_subject: bool,
) -> bool:
    """Create a subject for the given semester/year if the semester exists.

    Returns True if the semester was found (subject may or may not be
    newly created). Returns False if the semester does not exist.
    """
    sem = session.exec(
        select(Semester).where(
            Semester.name == semester,
            Semester.year == int(year) if str(year).isdigit() else Semester.year == Semester.year,
        )
    ).first()
    semester_id = getattr(sem, "id", None)

    if semester_id is None:
        return False

    exists = session.exec(
        select(Subject).where(
            Subject.semester_id == semester_id,
            Subject.subject_code == subject_code,
        )
    ).first()
    if not exists:
        session.add(
            Subject(
                semester_id=semester_id,
                subject_code=subject_code,
                subject_name=subject_name,
                credit_points=credit_points,
                has_exam=bool(has_exam),
                sync_subject=bool(sync_subject),
            )
        )
        session.commit()

    return True


def add_prerequisite_core(
    session: Session,
    semester: str,
    year: str,
    code: str,
    prerequisite_subject_id: Optional[str],
    custom_prerequisite: Optional[str],
    is_corequisite: Optional[str],
) -> str:
    """Core logic for adding a prerequisite.

    Returns a status string:
    - "ok" on success (or benign no-op)
    - "semester_not_found" if the semester does not exist
    - "subject_not_found" if the subject does not exist
    """
    import logging
    logger = logging.getLogger("uvicorn.error")
    
    logger.info(f"[ADD_PREREQ_DEBUG] semester={semester}, year={year}, code={code}, prereq_id={prerequisite_subject_id}, custom={custom_prerequisite}, coreq={is_corequisite}")
    
    try:
        year_int = int(str(year))
    except Exception:
        year_int = None

    sem = None
    if year_int is not None:
        sem = session.exec(
            select(Semester).where(
                Semester.name == semester,
                Semester.year == year_int,
            )
        ).first()

    if not sem or getattr(sem, "id", None) is None:
        logger.error(f"[ADD_PREREQ_DEBUG] Semester not found: {semester}, {year_int}")
        return "semester_not_found"

    subject = session.exec(
        select(Subject).where(
            Subject.semester_id == sem.id,  # type: ignore[arg-type]
            Subject.subject_code == code,
        )
    ).first()
    if not subject or getattr(subject, "id", None) is None:
        logger.error(f"[ADD_PREREQ_DEBUG] Subject not found: {code} in semester {sem.id}")
        return "subject_not_found"

    mgr = SubjectPrerequisiteManager(session)

    # Prefer linking to an existing subject via dropdown when provided
    if prerequisite_subject_id:
        try:
            prereq_id = int(prerequisite_subject_id)
            logger.info(f"[ADD_PREREQ_DEBUG] Adding prerequisite: subject_id={subject.id}, prereq_subject_id={prereq_id}, coreq={is_corequisite}")
            mgr.add_prerequisite(
                subject_id=int(subject.id),  # type: ignore[arg-type]
                prerequisite_subject_id=prereq_id,
                is_corequisite=bool(int(is_corequisite or "0")),
            )
            logger.info(f"[ADD_PREREQ_DEBUG] Successfully added prerequisite")
        except Exception as e:
            logger.error(f"[ADD_PREREQ_DEBUG] Failed to add prerequisite: {e}", exc_info=True)
            pass
    # Otherwise, fall back to storing a custom free-text prerequisite
    elif custom_prerequisite and custom_prerequisite.strip():
        try:
            logger.info(f"[ADD_PREREQ_DEBUG] Adding custom prerequisite: subject_id={subject.id}, custom_text={custom_prerequisite}")
            mgr.add_prerequisite(
                subject_id=int(subject.id),  # type: ignore[arg-type]
                prerequisite_subject_id=None,
                custom_text=custom_prerequisite.strip(),
                is_corequisite=bool(int(is_corequisite or "0")),
            )
            logger.info(f"[ADD_PREREQ_DEBUG] Successfully added custom prerequisite")
        except Exception as e:
            logger.error(f"[ADD_PREREQ_DEBUG] Failed to add custom prerequisite: {e}", exc_info=True)
            pass
    else:
        logger.warn(f"[ADD_PREREQ_DEBUG] No prerequisite_subject_id or custom_prerequisite provided")

    return "ok"
