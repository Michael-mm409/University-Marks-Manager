"""Examination API endpoints (single exam per subject)."""
from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from src.infrastructure.db.models import Examination, Assignment
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
    existing = session.exec(
        select(Examination).where(
            Examination.subject_code == data.subject_code,
            Examination.semester_name == data.semester_name,
            Examination.year == data.year,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Exam already exists for subject")

    # infer exam_weight if needed from remaining weight after assignments
    if not data.exam_weight:
        assignments = session.exec(
            select(Assignment).where(
                Assignment.subject_code == data.subject_code,
                Assignment.semester_name == data.semester_name,
                Assignment.year == data.year,
            )
        ).all()
        used = 0.0
        for a in assignments:
            if a.mark_weight:
                try:
                    used += float(a.mark_weight)
                except ValueError:
                    pass
        data.exam_weight = max(0.0, 100.0 - used)

    exam = Examination(**data.model_dump(exclude={"id"}))
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam


@router.get("/{exam_id}", response_model=ExaminationRead)
def get_exam(exam_id: int, session: Session = Depends(get_session)) -> Examination:
    """
    Retrieve an examination by its ID.
    
    Args:
        exam_id (int): The ID of the examination to retrieve.
        session (Session): Database session dependency.

    Raises:
        HTTPException: If the examination is not found (404).
    
    Returns:
        Examination: The requested examination.
    """
    exam = session.get(Examination, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Not found")
    return exam


@router.put("/{exam_id}", response_model=ExaminationRead)
def update_exam(exam_id: int, data: ExaminationCreate,
                session: Session = Depends(get_session)) -> Examination:
    """
    Update an existing examination's details.
    
    Args:
        exam_id (int): The ID of the examination to update.
        data (Examination): Updated examination data.
        session (Session): Database session dependency.
    
    Raises:
        HTTPException: If the examination is not found (404).
    
    Returns:
        Examination: The updated examination.
    """
    exam = session.get(Examination, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Not found")
    exam.exam_mark = data.exam_mark
    exam.exam_weight = data.exam_weight or exam.exam_weight
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam

@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_exam(exam_id: int, session: Session = Depends(get_session)) -> Response:
    """
    Delete an examination by its ID.
    
    Args:
        exam_id (int): The ID of the examination to delete.
        session (Session): Database session dependency.

    Raises:
        HTTPException: If the examination is not found (404).
    
    """
    exam = session.get(Examination, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(exam)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

__all__ = ["router"]
