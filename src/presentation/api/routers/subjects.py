"""Subject API endpoints."""
from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from src.infrastructure.db.models import Subject
from src.presentation.api.schemas import SubjectCreate, SubjectRead
from src.presentation.api.deps import get_session

router = APIRouter()


@router.get("/", response_model=List[SubjectRead])
def list_subjects(
	session: Session = Depends(get_session),
	semester_name: Optional[str] = None,
	year: Optional[str] = None,
	code: Optional[str] = None,
) -> Sequence[Subject]:
    """
    List all subjects, optionally filtered by semester name, year, and subject code.
    Args:
        session (Session): Database session dependency.
        semester_name (Optional[str]): Semester name to filter subjects by.
        year (Optional[str]): Year to filter subjects by.
        code (Optional[str]): Subject code to filter subjects by.
    
	Returns:
        Sequence[Subject]: List of subjects.
    """
    stmt = select(Subject)
    if semester_name:
        stmt = stmt.where(Subject.semester_name == semester_name)
    if year:
        stmt = stmt.where(Subject.year == year)
    if code:
        stmt = stmt.where(Subject.subject_code == code)
    return session.exec(stmt).all()


@router.post("/", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(data: SubjectCreate, session: Session = Depends(get_session)) -> Subject:
    """
	Create a new subject if it does not already exist in the specified semester and year.
	
	Args:
        data (Subject): Subject data to create.
		session (Session): Database session dependency.
    
    Raises:
        HTTPException: If the subject already exists in the specified semester and year (409).
    
    Returns:
        Subject: The created subject.
	"""
    exists = session.exec(
        select(Subject).where(
            Subject.subject_code == data.subject_code,
            Subject.semester_name == data.semester_name,
            Subject.year == data.year,
        )
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Subject already exists in semester/year")
    subj = Subject(
        subject_code=data.subject_code,
        subject_name=data.subject_name,
        semester_name=data.semester_name,
        year=data.year,
        total_mark=data.total_mark,
        sync_subject=data.sync_subject,
    )
    session.add(subj)
    session.commit()
    session.refresh(subj)
    return subj


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
    
    Returns:
        Subject: The updated subject.
    """
    subj = session.get(Subject, subject_id)
    if not subj:
        raise HTTPException(status_code=404, detail="Not found")
    subj.subject_code = data.subject_code
    subj.subject_name = data.subject_name
    subj.semester_name = data.semester_name
    subj.year = data.year
    subj.total_mark = data.total_mark
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
