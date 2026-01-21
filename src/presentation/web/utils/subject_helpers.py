from __future__ import annotations

from typing import List, Optional
import re

from sqlmodel import Session, select, col

from src.core.services.subject_prerequisite_manager import SubjectPrerequisiteManager
from src.infrastructure.db.models import Subject, Semester


def infer_level_from_text(text: str) -> Optional[int]:
    """Infer an integer level (1,2,3,...) from a subject code or free-text.

    Examples:
    - "CSIT110" -> 1
    - "MATH221" -> 2
    - "18cp @ 200 level" -> 2
    """
    if not text:
        return None
    # Look for a 3-digit number (e.g. 110, 221)
    m = re.search(r"(\d{3})", text)
    if m:
        try:
            val = int(m.group(1))
            return max(1, val // 100)
        except ValueError:
            pass
    # Look for explicit "100 level", "200 level", etc.
    m2 = re.search(r"(100|200|300|400|500|600)\s*level", text)
    if m2:
        try:
            val = int(m2.group(1))
            return max(1, val // 100)
        except ValueError:
            pass
    return None


def resolve_subject_for_context(
    session: Session,
    semester: str,
    year: str,
    code: str,
) -> Optional[Subject]:
    """Resolve the concrete Subject for a given semester/year/code.

    This encapsulates year parsing and Semester lookup so callers can
    focus on computing marks and prerequisite context.
    """
    try:
        year_int = int(str(year))
    except Exception:
        try:
            year_int = int(str(year).strip())
        except Exception:
            year_int = None

    if year_int is None:
        return None

    sem = session.exec(
        select(Semester).where(
            Semester.name == semester,
            Semester.year == year_int,
        )
    ).first()

    if not sem or getattr(sem, "id", None) is None:
        return None

    subject = session.exec(
        select(Subject).where(
            Subject.semester_id == sem.id,  # type: ignore[arg-type]
            Subject.subject_code == code,
        )
    ).first()
    return subject


def build_candidate_subjects(session: Session, subject: Optional[Subject]) -> List[Subject]:
    """Return candidate prerequisite subjects for the given subject.

    This discovers all subjects in the same course (across semesters)
    that are not already prerequisites of the current subject.
    """
    candidate_subjects: List[Subject] = []

    if subject is None or subject.id is None:
        return candidate_subjects

    # Find the semester and course for this subject
    sem = session.exec(
        select(Semester).where(Semester.id == subject.semester_id)
    ).first()

    if sem is None or getattr(sem, "course_id", None) is None:
        return candidate_subjects

    course_id = sem.course_id
    # Collect all semesters for this course
    semester_ids = [
        row
        for row in session.exec(
            select(Semester.id).where(Semester.course_id == course_id)
        ).all()
        if row is not None
    ]

    if not semester_ids:
        return candidate_subjects

    # All subjects across these semesters
    all_subjects = session.exec(
        select(Subject).where(col(Subject.semester_id).in_(semester_ids))
    ).all()

    prereq_manager = SubjectPrerequisiteManager(session)
    existing_prereqs = prereq_manager.get_prerequisites(int(subject.id))

    existing_prereq_ids = {
        s.id for s in existing_prereqs if s.id is not None
    }

    candidate_subjects = [
        s
        for s in all_subjects
        if s.id is not None
        and s.id != subject.id
        and s.id not in existing_prereq_ids
    ]

    return candidate_subjects
