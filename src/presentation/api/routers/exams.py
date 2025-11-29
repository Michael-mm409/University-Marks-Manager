"""Examination API endpoints (single exam per subject)."""
from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from src.infrastructure.db.models import Examination, Assignment, Subject
from src.presentation.api.schemas import ExaminationCreate, ExaminationRead
from src.presentation.api.deps import get_session

router = APIRouter()
@router.get("/", response_model=List[ExaminationRead])
def list_exams(
    session: Session = Depends(get_session),
    subject_code: Optional[str] = None,
    semester_name: Optional[str] = None,
    year: Optional[str] = None,
) -> Sequence[Examination]:
    """
    List all exams, optionally filtered by subject code, semester name, and year.
    
    Args:
        session (Session): Database session dependency.
        subject_code (Optional[str]): Subject code to filter exams by.
        semester_name (Optional[str]): Semester name to filter exams by.
        year (Optional[str]): Year to filter exams by.
    Returns:
        Sequence[Examination]: List of examinations.
    """
    # Prefer normalized filtering when all three are provided
    if subject_code and semester_name and year:
        subj = session.exec(
            select(Subject).where(
                Subject.subject_code == subject_code,
                Subject.semester_name == semester_name,
                Subject.year == year,
            )
        ).first()
        sid = getattr(subj, "id", None)
        if sid is not None:
            return session.exec(select(Examination).where(Examination.subject_id == sid)).all()
    # Fallback legacy partial filters
    stmt = select(Examination)
    if subject_code:
        stmt = stmt.where(Examination.subject_code == subject_code)
    if semester_name:
        stmt = stmt.where(Examination.semester_name == semester_name)
    if year:
        stmt = stmt.where(Examination.year == year)
    return session.exec(stmt).all()


@router.post("/", response_model=ExaminationRead, status_code=status.HTTP_201_CREATED)
def create_exam(data: ExaminationCreate, session: Session = Depends(get_session)) -> Examination:
    """
    Create a new examination record if one does not already exist for the subject in the given semester/year.

    Args:
        data (Examination): Examination data to create.
        session (Session): Database session dependency.
        
    Raises:
        HTTPException: If an exam already exists for the subject in the specified semester/year.

    Returns:
        Examination: The created examination.
    """
    # Resolve subject_id, enforce one-exam-per-subject
    subj = session.exec(
        select(Subject).where(
            Subject.subject_code == data.subject_code,
            Subject.semester_name == data.semester_name,
            Subject.year == data.year,
        )
    ).first()
    sid = getattr(subj, "id", None)
    existing = session.exec(select(Examination).where(Examination.subject_id == sid)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Exam already exists for subject")

    # infer exam_weight if needed from remaining weight after assignments
    if not data.exam_weight:
        assignments = session.exec(
            select(Assignment).where(
                Assignment.subject_id == sid
            ).order_by(Assignment.assessment)
        ).all()
        used = 0.0
        for a in assignments:
            if a.mark_weight:
                try:
                    used += float(a.mark_weight)
                except ValueError:
                    pass
        data.exam_weight = max(0.0, 100.0 - used)

    # Exclude None values so SQLModel will use the model defaults for non-optional fields
    payload = data.model_dump(exclude_none=True, exclude={"id"})
    payload["subject_id"] = sid
    exam = Examination(**payload)
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam


@router.get("/{year}/{subject_code}/{semester_name}", response_model=ExaminationRead)
def get_exam(
    year: str,
    subject_code: str,
    semester_name: str,
    session: Session = Depends(get_session),
) -> Examination:
    """
    Retrieve an examination by its composite primary key (subject_code, semester_name, year).
    """
    # Prefer normalized lookup by subject_id; fallback to composite if not found
    subj = session.exec(
        select(Subject).where(
            Subject.subject_code == subject_code,
            Subject.semester_name == semester_name,
            Subject.year == year,
        )
    ).first()
    sid = getattr(subj, "id", None)
    exam = None
    if sid is not None:
        exam = session.exec(select(Examination).where(Examination.subject_id == sid)).first()
    if not exam:
        exam = session.get(Examination, (subject_code, semester_name, year))
    if not exam:
        raise HTTPException(status_code=404, detail="Not found")
    return exam


@router.put("/{year}/{subject_code}/{semester_name}", response_model=ExaminationRead)
def update_exam(
    year: str,
    subject_code: str,
    semester_name: str,
    data: ExaminationCreate,
    session: Session = Depends(get_session),
) -> Examination:
    """
    Update an existing examination's details identified by its composite primary key.
    """
    # Prefer normalized lookup by subject_id; fallback to composite if not found
    subj = session.exec(
        select(Subject).where(
            Subject.subject_code == subject_code,
            Subject.semester_name == semester_name,
            Subject.year == year,
        )
    ).first()
    sid = getattr(subj, "id", None)
    exam = None
    if sid is not None:
        exam = session.exec(select(Examination).where(Examination.subject_id == sid)).first()
    if not exam:
        exam = session.get(Examination, (subject_code, semester_name, year))
    if not exam:
        raise HTTPException(status_code=404, detail="Not found")
    # Only assign exam_mark if the client provided a value (it may be optional in the schema)
    if data.exam_mark is not None:
        exam.exam_mark = data.exam_mark
    # exam_weight may be omitted; fall back to existing value if not provided
    exam.exam_weight = data.exam_weight if data.exam_weight is not None else exam.exam_weight
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam


@router.delete("/{year}/{subject_code}/{semester_name}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_exam(
    year: str,
    subject_code: str,
    semester_name: str,
    session: Session = Depends(get_session),
) -> Response:
    """
    Delete an examination by its composite primary key.
    """
    exam = session.get(Examination, (subject_code, semester_name, year))
    if not exam:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(exam)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["router"]