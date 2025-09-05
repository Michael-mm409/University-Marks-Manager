"""Semester API endpoints."""
from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from src.infrastructure.db.models import Semester
from src.presentation.api.deps import get_session

router = APIRouter()


@router.get("/", response_model=List[Semester])
def list_semesters(session: Session = Depends(get_session), year: Optional[str] = None) -> Sequence[Semester]:
    """
    List all semesters, optionally filtered by year.
    
    Args:
        session (Session): Database session dependency.
        year (Optional[str]): Year to filter semesters by.
        
    Returns:
        Sequence[Semester]: List of semesters.
    """
    stmt = select(Semester)
    if year:
        stmt = stmt.where(Semester.year == year)
    return session.exec(stmt).all()


@router.post("/", response_model=Semester, status_code=status.HTTP_201_CREATED)
def create_semester(data: Semester, session: Session = Depends(get_session)) -> Semester:
    """
    Create a new semester if it does not already exist.
    
    Args:
        data (Semester): Semester data to create.
        session (Session): Database session dependency.
    
    Returns:
        Semester: The created semester.
    """
    exists = session.exec(
        select(Semester).where(Semester.name == data.name, Semester.year == data.year)
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Semester already exists")
    sem = Semester(name=data.name, year=data.year)
    session.add(sem)
    session.commit()
    session.refresh(sem)
    return sem


@router.get("/{semester_id}", response_model=Semester)
def get_semester(semester_id: int, session: Session = Depends(get_session)) -> Semester:
    """
    Retrieve a semester by its ID.

    Args:
        semester_id (int): The ID of the semester to retrieve.
        session (Session): Database session dependency.
    
    Returns:
        Semester: The requested semester.
    """
    sem = session.get(Semester, semester_id)
    if not sem:
        raise HTTPException(status_code=404, detail="Not found")
    return sem

@router.put("/{semester_id}", response_model=Semester)
def update_semester(semester_id: int, data: Semester, session: Session = Depends(get_session)) -> Semester:
    """
    Update an existing semester's details.
    
    Args:
        semester_id (int): The ID of the semester to update.
        data (Semester): Updated semester data.
        session (Session): Database session dependency.
    
    Returns:
        Semester: The updated semester.
    """
    sem = session.get(Semester, semester_id)
    if not sem:
        raise HTTPException(status_code=404, detail="Not found")
    sem.name = data.name
    sem.year = data.year
    session.add(sem)
    session.commit()
    session.refresh(sem)
    return sem

@router.delete("/{semester_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_semester(semester_id: int, session: Session = Depends(get_session)) -> Response:
    """
    Delete a semester by its ID.
    
    Args:
        semester_id (int): The ID of the semester to delete.
        session (Session): Database session dependency.
    """
    sem = session.get(Semester, semester_id)
    if not sem:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(sem)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

__all__ = ["router"]
