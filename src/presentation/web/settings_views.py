from typing import List, Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select, delete, desc

from src.presentation.api.deps import get_session
from src.infrastructure.db.models import GradeScale, Course
from src.presentation.web.template_helpers import _render
from src.core.services.grade_calculator import GradeCalculator

router = APIRouter()

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, session: Session = Depends(get_session)):
    """Render the settings page."""
    # Determine active course to show its scale
    sess = request.session
    active_course_id = sess.get("current_course_id")
    
    current_scale_name = "Standard"
    course = None
    
    if active_course_id:
        course = session.get(Course, active_course_id)
        if course and course.grading_scale:
            current_scale_name = course.grading_scale

    # Ensure defaults exist for this scale (via calculator logic)
    gc = GradeCalculator(session)
    gc._get_grade_scales(active_course_id)
    
    # Fetch scales for the current scale name
    scales = session.exec(
        select(GradeScale)
        .where(GradeScale.scale_name == current_scale_name)
        .order_by(desc(GradeScale.min_mark))
    ).all()
    
    return _render(request, "settings.html", {
        "scales": scales,
        "current_scale_name": current_scale_name,
        "course": course
    })

@router.post("/settings/grades/update")
def update_grades(
    request: Request,
    scale_name: str = Form(...),
    grades: List[str] = Form(...),
    labels: List[str] = Form(...),
    min_marks: List[float] = Form(...),
    gpa_points: List[float] = Form(...),
    session: Session = Depends(get_session)
):
    """Update grade scales for a specific scale name."""
    # Remove existing scales for this scale_name
    query = delete(GradeScale).where(GradeScale.scale_name == scale_name)  # type: ignore
    session.execute(query)
    
    # Re-insert
    for g, l, m, p in zip(grades, labels, min_marks, gpa_points):
        if not g.strip(): 
            continue
        
        scale = GradeScale(
            scale_name=scale_name,
            grade=g.strip(), 
            label=l.strip(), 
            min_mark=m, 
            gpa_point=p
        )
        session.add(scale)
        
    session.commit()
    
    request.session["flash_message"] = f"Grade scales for '{scale_name}' updated successfully."
    return RedirectResponse(url="/settings", status_code=303)
