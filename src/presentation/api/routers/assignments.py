"""Assignment API endpoints."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from src.infrastructure.db.models import Assignment, GradeType
from src.presentation.api.schemas import AssignmentCreate, AssignmentRead
from src.presentation.api.deps import get_session

router = APIRouter()


@router.api_route("/", response_model=List[AssignmentRead], methods=["GET", "HEAD"])
def list_assignments(
    session: Session = Depends(get_session),
    subject_code: Optional[str] = None,
    semester_name: Optional[str] = None,
    year: Optional[str] = None,
):
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
    stmt = select(Assignment).order_by(Assignment.assessment)
    if subject_code:
        stmt = stmt.where(Assignment.subject_code == subject_code)
    if semester_name:
        stmt = stmt.where(Assignment.semester_name == semester_name)
    if year:
        stmt = stmt.where(Assignment.year == year)
    return session.exec(stmt).all()


@router.api_route("/", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED, methods=["POST"])
def create_assignment(data: AssignmentCreate, session: Session = Depends(get_session)):
    """
    Create a new assignment.

    Args:
        data (Assignment): Assignment data to create.
        session (Session): Database session dependency.

    Returns:
        Assignment: The created assignment.
    """
    # For numeric grades compute unweighted when possible
    if (
        data.grade_type == GradeType.NUMERIC.value
        and data.weighted_mark is not None
        and data.mark_weight not in (None, 0)
    ):
        try:
            weighted_val = float(data.weighted_mark)
            weight = float(data.mark_weight)
            # weight parsed; division-by-zero is guarded by `if weight:` below
            if weight:
                data.unweighted_mark = round(weighted_val / weight, 4)
        except (ValueError, TypeError):
            pass
    # Safely obtain a dict payload from the SQLModel/Pydantic object. Some language servers
    # may not recognize `model_dump` (pydantic v2). Fall back to `dict` when needed.
    if hasattr(data, "model_dump"):
        payload = data.model_dump(exclude={"id"})
    else:
        payload = data.dict(exclude={"id"})
    # Ensure weighted_mark is numeric (float) when provided. The schema uses Optional[float].
    if payload.get("weighted_mark") is not None:
        try:
            payload["weighted_mark"] = float(payload["weighted_mark"])
        except Exception:
            # If conversion fails, leave as-is and let the ORM/DB raise if invalid
            pass
    duplicate = session.exec(
        select(Assignment).where(
            Assignment.assessment == payload["assessment"],
            Assignment.subject_code == payload["subject_code"],
            Assignment.semester_name == payload["semester_name"],
            Assignment.year == payload["year"],
        )
    ).first()
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Assignment already exists")
    duplicate = session.exec(
        select(Assignment).where(
            Assignment.assessment == payload["assessment"],
            Assignment.subject_code == payload["subject_code"],
            Assignment.semester_name == payload["semester_name"],
            Assignment.year == payload["year"],
        )
    ).first()

    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Assignment already exists")
    assignment = Assignment(**payload)
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@router.api_route("/{assignment_id}", response_model=AssignmentRead, methods=["GET", "HEAD"])
def get_assignment(assignment_id: int, session: Session = Depends(get_session)):
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


@router.api_route("/{assignment_id}", response_model=AssignmentRead, methods=["PUT"])
def update_assignment(assignment_id: int, data: AssignmentCreate,
                      session: Session = Depends(get_session)):
    """
    Update an existing assignment's details.
    
    Args:
        assignment_id (int): The ID of the assignment to update.
        data (Assignment): Updated assignment data.
        session (Session): Database session dependency.
    
    Raises:
        HTTPException: If the assignment is not found (404).
    
    Returns:
        if (
            a.grade_type == GradeType.NUMERIC.value
            and a.weighted_mark is not None
            and a.mark_weight not in (None, 0)
        ):
            try:
                weighted_val = float(a.weighted_mark)
                weight = float(a.mark_weight)
                if weight:
                    a.unweighted_mark = round(weighted_val / weight, 4)
            except (ValueError, TypeError):
                pass
        Assignment: The updated assignment.
    """
    assignment_record = session.get(Assignment, assignment_id)
    if not assignment_record:
        raise HTTPException(status_code=404, detail="Not found")
    # Safely obtain payload dict (see create_assignment note)
    if hasattr(data, "model_dump"):
        payload = data.model_dump(exclude={"id"})
    else:
        payload = data.dict(exclude={"id"})
    # Ensure weighted_mark is numeric (float) when provided
    if payload.get("weighted_mark") is not None:
        try:
            payload["weighted_mark"] = float(payload["weighted_mark"])
        except (ValueError, TypeError):
            pass
    # Guard against creating a duplicate natural key (exclude the current record)
    duplicate = session.exec(
        select(Assignment).where(
            Assignment.id != assignment_id,
            Assignment.assessment == payload["assessment"],
            Assignment.subject_code == payload["subject_code"],
            Assignment.semester_name == payload["semester_name"],
            Assignment.year == payload["year"],
        )
    ).first()
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Assignment already exists")
    for field, value in payload.items():
        setattr(assignment_record, field, value)
    # recompute unweighted if numeric
    if (
        assignment_record.grade_type == GradeType.NUMERIC.value
        and assignment_record.weighted_mark is not None
        and assignment_record.mark_weight not in (None, 0)
    ):
        try:
            weighted_val = float(assignment_record.weighted_mark)
            weight = float(assignment_record.mark_weight)
            if weight:
                assignment_record.unweighted_mark = round(weighted_val / weight, 4)
        except (ValueError, TypeError):
            pass
    session.add(assignment_record)
    session.commit()
    session.refresh(assignment_record)
    return assignment_record


@router.api_route("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, methods=["DELETE"])
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
