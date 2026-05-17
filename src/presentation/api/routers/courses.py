"""API router for managing courses."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlmodel import Session

from src.core.services.course_manager import CourseManager
from src.infrastructure.db.engine import get_session
from src.infrastructure.db.models import Course


# Pydantic models for request/response
class CourseCreate(BaseModel):
    """Request model for creating a course."""
    name: str
    code: str | None = None
    university_id: int | None = None
    new_university_name: str | None = None
    grading_scale_id: int = 1


class CourseRead(BaseModel):
    """Response model for reading a course."""
    id: int
    name: str
    code: str | None
    university_id: int | None = None


# API Router
courses_router = APIRouter(prefix="/courses", tags=["Courses"])


@courses_router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    session: Session = Depends(get_session),
) -> Course:
    """Create a new course, creating a university if needed."""
    normalized_code = (course_data.code or "").strip()
    if not normalized_code:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="course code is required")

    university_id = course_data.university_id
    if course_data.university_id == None and course_data.new_university_name:
        # Try to find or create the university
        from src.infrastructure.db.models import University
        from sqlmodel import select
        uni_name = course_data.new_university_name.strip()
        if not uni_name:
            raise HTTPException(status_code=422, detail="University name required")
        existing = session.exec(select(University).where(University.name == uni_name)).first()
        if existing:
            university_id = existing.id
        else:
            new_uni = University(name=uni_name)
            session.add(new_uni)
            session.commit()
            session.refresh(new_uni)
            university_id = new_uni.id

    course_manager = CourseManager(session)
    course = course_manager.create_course(name=course_data.name, code=normalized_code, grading_scale_id=course_data.grading_scale_id, university_id=university_id)
    return course


@courses_router.get("/", response_model=List[CourseRead])
def get_all_courses(session: Session = Depends(get_session)) -> List[Course]:  # noqa: B008
    """Get a list of all courses."""
    course_manager = CourseManager(session)
    courses = course_manager.get_all_courses()
    return courses


class CourseCodeDebug(BaseModel):
    """
    Short description of the class.

    Attributes:
        attr1: Description.
    """
    id: int
    name: str
    code_raw: str | None
    code_len: int
    trimmed: str
    trim_len: int


@courses_router.get("/_codes")
def list_course_codes(request: Request, session: Session = Depends(get_session)):  # noqa: B008
    """List raw and trimmed course codes, plus potential TRIM+lower collisions (JSON)."""
    # Gate via app state flag and optional debug token
    enabled = getattr(request.app.state, "enable_debug_routes", False)
    token = getattr(request.app.state, "debug_token", None)
    if not enabled:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    if token and request.query_params.get("token") != token:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    cm = CourseManager(session)
    courses = cm.get_all_courses()
    rows: list[CourseCodeDebug] = []
    for c in courses:
        code = c.code or ""
        trimmed = code.strip()
        rows.append(
            CourseCodeDebug(
                id=int(c.id or 0),
                name=c.name,
                code_raw=c.code,
                code_len=len(code),
                trimmed=trimmed,
                trim_len=len(trimmed),
            )
        )
    # collisions after TRIM+lower
    from collections import defaultdict
    buckets = defaultdict(list)
    for c in courses:
        norm = (c.code or "").strip().lower()
        if norm:
            buckets[norm].append(c)
    collisions = [
        {
            "key": k,
            "ids": [c.id for c in vs],
            "codes": [c.code for c in vs],
        }
        for k, vs in buckets.items()
        if len(vs) > 1
    ]
    return {
        "total": len(rows),
        "rows": [r.model_dump() for r in rows],
        "collisions": collisions,
    }


@courses_router.get("/by-code/{code}", response_model=CourseRead)
def get_course_by_code_api(code: str, session: Session = Depends(get_session)) -> Course:  # noqa: B008
    """Resolve a course by its code (case-insensitive, trimmed)."""
    cm = CourseManager(session)
    course = cm.get_course_by_code(code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
