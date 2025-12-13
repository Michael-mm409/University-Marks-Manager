"""Subject API endpoints."""
from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
    # No need for and_ import unless using multiple join conditions

from src.infrastructure.db.models import Subject, Semester
from src.presentation.api.schemas import SubjectCreate, SubjectRead
from src.presentation.api.deps import get_session

from sqlalchemy.sql import expression

router = APIRouter()


@router.get("/", response_model=List[SubjectRead])
def list_subjects(
    session: Session = Depends(get_session),
    semester_id: Optional[int] = None,
    semester_name: Optional[str] = None,
    year: Optional[int] = None,
    code: Optional[str] = None,
) -> Sequence[Subject]:
    """
    List all subjects, optionally filtered by semester name, year, and subject code.
    Args:
        session (Session): Database session dependency.
        semester_name (Optional[str]): Semester name to filter subjects by.
        year (Optional[int]): Year to filter subjects by.
        code (Optional[str]): Subject code to filter subjects by.
    
    Returns:
        Sequence[Subject]: List of subjects.
    """
    stmt = select(Subject)
    # Prefer normalized filter by semester_id
    if semester_id is not None:
        stmt = stmt.where(Subject.semester_id == semester_id)
    elif semester_name or year:
        # Join on semester_id to Semester.id, then filter by Semester.name/year
        stmt = stmt.join(Semester, expression.true() & (Subject.semester_id == Semester.id))
        if semester_name:
            stmt = stmt.where(Semester.name == semester_name)
        if year:
            stmt = stmt.where(Semester.year == year)
    if code:
        stmt = stmt.where(Subject.subject_code == code)
    return session.exec(stmt).all()


@router.post("/", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(data: SubjectCreate, session: Session = Depends(get_session)) -> Subject:
    """
    Create a new subject in a specific semester (normalized: uses semester_id).

    Args:
        data (Subject): Subject data to create.
        session (Session): Database session dependency.
    
    Raises:
        HTTPException: If the subject already exists in the semester (409).
        HTTPException: If the semester_id is invalid (400).
    
    Returns:
        Subject: The created subject.
    """
    # Validate semester exists
    sem = session.get(Semester, data.semester_id)
    if not sem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="semester not found")

    # Enforce uniqueness: (subject_code, semester_id)
    exists = session.exec(
        select(Subject).where(
            Subject.subject_code == data.subject_code,
            Subject.semester_id == data.semester_id,
        )
    ).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="subject already exists for semester")

    # Ensure semester_year is always an int (fallback to semester.year if not provided)
    semester_year = getattr(data, 'semester_year', None)
    if semester_year is None and sem:
        semester_year = sem.year
    if semester_year is None:
        raise HTTPException(status_code=400, detail="semester_year is required")
    sub = Subject(
        subject_code=data.subject_code,
        subject_name=data.subject_name,
        semester_id=data.semester_id,
        semester_year=int(semester_year),
        sync_subject=data.sync_subject,
        total_mark=data.total_mark,
    )
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


@router.get("/{subject_id}", response_model=SubjectRead)
def get_subject(subject_id: int, session: Session = Depends(get_session)) -> Subject:
    """
    Retrieve a subject by its ID.
    
    Args:
        subject_id (int): The ID of the subject to retrieve.
        session (Session): Database session dependency.
    
    Raises:
        HTTPException: If the subject is not found (404).
    
    Returns:
        Subject: The requested subject.
    """
    subj = session.get(Subject, subject_id)
    if not subj:
        raise HTTPException(status_code=404, detail="Not found")
    return subj


@router.put("/{subject_id}", response_model=SubjectRead)
def update_subject(subject_id: int, data: SubjectCreate, session: Session = Depends(get_session)) -> Subject:
    """
    Update an existing subject's details.

    Args:
        subject_id (int): The ID of the subject to update.
        data (Subject): Updated subject data.
        session (Session): Database session dependency.
    
    Raises:
        HTTPException: If the subject is not found (404).
        HTTPException: If another subject with same code/semester exists (409).
        HTTPException: If the semester_id is invalid (400).
    
    Returns:
        Subject: The updated subject.
    """
    subj = session.get(Subject, subject_id)
    if not subj:
        raise HTTPException(status_code=404, detail="Not found")

    # Verify semester exists
    semester = session.get(Semester, data.semester_id)
    if not semester:
        raise HTTPException(status_code=400, detail="Invalid semester_id")

    # Check if another subject with the same identifiers exists
    exists = session.exec(
        select(Subject).where(
            Subject.subject_code == data.subject_code,
            Subject.semester_id == data.semester_id,
            Subject.id != subject_id,
        )
    ).first()
    
    if exists:
        raise HTTPException(status_code=409, detail="Another subject with same code/semester exists")

    subj.subject_code = data.subject_code
    subj.subject_name = data.subject_name
    subj.semester_id = data.semester_id
    subj.total_mark = data.total_mark if data.total_mark is not None else subj.total_mark
    # credit_points is not part of SubjectCreate (normalized); keep existing value
    if hasattr(data, 'sync_subject'):
        subj.sync_subject = data.sync_subject
    session.add(subj)
    session.commit()
    session.refresh(subj)
    return subj

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_subject(subject_id: int, session: Session = Depends(get_session)) -> Response:
    """
    Delete a subject by its ID.

    Args:
        subject_id (int): The ID of the subject to delete.
        session (Session): Database session dependency.

    Raises:
        HTTPException: If the subject is not found (404).
    """
    subj = session.get(Subject, subject_id)
    if not subj:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(subj)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

__all__ = ["router"]
