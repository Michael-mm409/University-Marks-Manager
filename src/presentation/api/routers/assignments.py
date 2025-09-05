"""Assignment API endpoints."""
from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from src.infrastructure.db.models import Assignment, GradeType
from src.presentation.api.deps import get_session

router = APIRouter()


@router.get("/", response_model=List[Assignment])
def list_assignments(
	session: Session = Depends(get_session),
	subject_code: Optional[str] = None,
	semester_name: Optional[str] = None,
	year: Optional[str] = None,
) -> Sequence[Assignment]:
    """
    List all assignments, optionally filtered by subject code, semester name, and year.

    Args:
        session (Session): Database session dependency.
        subject_code (Optional[str]): Subject code to filter assignments by.
        semester_name (Optional[str]): Semester name to filter assignments by.
        year (Optional[str]): Year to filter assignments by.
        
    Returns:
        Sequence[Assignment]: List of assignments.
    """
    stmt = select(Assignment)
    if subject_code:
        stmt = stmt.where(Assignment.subject_code == subject_code)
    if semester_name:
        stmt = stmt.where(Assignment.semester_name == semester_name)
    if year:
        stmt = stmt.where(Assignment.year == year)
    return session.exec(stmt).all()


@router.post("/", response_model=Assignment, status_code=status.HTTP_201_CREATED)
def create_assignment(data: Assignment, session: Session = Depends(get_session)) -> Assignment:
    """
    Create a new assignment.

    Args:
        data (Assignment): Assignment data to create.
        session (Session): Database session dependency.

    Returns:
        Assignment: The created assignment.
    """
    # For numeric grades compute unweighted when possible
    if data.grade_type == GradeType.NUMERIC.value and data.weighted_mark and data.mark_weight:
        try:
            weighted_val = float(data.weighted_mark)
            weight = float(data.mark_weight)
            if weight:
                data.unweighted_mark = round(weighted_val / weight, 4)
        except ValueError:
            pass
    assignment = Assignment(**data.model_dump(exclude={"id"}))
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@router.get("/{assignment_id}", response_model=Assignment)
def get_assignment(assignment_id: int, session: Session = Depends(get_session)) -> Assignment:
    """
    Retrieve an assignment by its ID.

    Args:
        assignment_id (int): The ID of the assignment to retrieve.
        session (Session): Database session dependency.

    Raises:
        HTTPException: If the assignment is not found (404).
    
    Returns:
        Assignment: The requested assignment.
    """
    a = session.get(Assignment, assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    return a


@router.put("/{assignment_id}", response_model=Assignment)
def update_assignment(assignment_id: int, data: Assignment, 
                      session: Session = Depends(get_session)) -> Assignment:
    """
    Update an existing assignment's details.
    
    Args:
        assignment_id (int): The ID of the assignment to update.
        data (Assignment): Updated assignment data.
        session (Session): Database session dependency.
    
    Raises:
        HTTPException: If the assignment is not found (404).
    
    Returns:
        Assignment: The updated assignment.
    """
    a = session.get(Assignment, assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in data.model_dump(exclude={"id"}).items():
        setattr(a, field, value)
    # recompute unweighted if numeric
    if a.grade_type == GradeType.NUMERIC.value and a.weighted_mark and a.mark_weight:
        try:
            weighted_val = float(a.weighted_mark)
            weight = float(a.mark_weight)
            if weight:
                a.unweighted_mark = round(weighted_val / weight, 4)
        except ValueError:
            pass
    session.add(a)
    session.commit()
    session.refresh(a)
    return a


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_assignment(assignment_id: int, session: Session = Depends(get_session)) -> Response:
    """
    Delete an assignment by its ID.
    
    Args:
        assignment_id (int): The ID of the assignment to delete.
        session (Session): Database session dependency.

    Raises:
        HTTPException: If the assignment is not found (404).
    """
    a = session.get(Assignment, assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(a)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

__all__ = ["router"]
