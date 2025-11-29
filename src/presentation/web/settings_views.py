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
    
    # Robustly resolve active course ID if it's missing or stringified
    if active_course_id is None:
        code = sess.get("current_course_code")
        if code:
            # Try to recover from code
            course_obj = session.exec(select(Course).where(Course.code == code)).first()
            if course_obj:
                active_course_id = course_obj.id
                # Heal session
                sess["current_course_id"] = active_course_id
    
    current_scale_name = "Standard"
    course = None
    
    if active_course_id:
        try:
            # Ensure it's an int
            cid = int(str(active_course_id))
            course = session.get(Course, cid)
            if course:
                # If course found, use its scale
                if course.grading_scale:
                    current_scale_name = course.grading_scale
            else:
                # ID in session but not in DB? Clear it to avoid confusion
                sess.pop("current_course_id", None)
        except (ValueError, TypeError):
            pass

    # Ensure defaults exist for this scale (via calculator logic)
    gc = GradeCalculator(session)
    # Pass the resolved ID (or None) to the calculator
    gc._get_grade_scales(course.id if course else None)
    
    # Fetch all available scale names
    all_scale_names = session.exec(select(GradeScale.scale_name).distinct()).all()
    # Fetch scales for the current scale name
    scales = session.exec(
        select(GradeScale)
        .where(GradeScale.scale_name == current_scale_name)
        .order_by(desc(GradeScale.min_mark))
    ).all()
    return _render(request, "settings.html", {
        "scales": scales,
        "current_scale_name": current_scale_name,
        "course": course,
        "all_scale_names": all_scale_names
    })


# Endpoint to update the grading scale for the active course
@router.post("/settings/scale/update")
def update_course_scale(
    request: Request,
    scale_name: str = Form(...),
    session: Session = Depends(get_session)
):
    sess = request.session
    active_course_id = sess.get("current_course_id")
    if active_course_id:
        try:
            cid = int(str(active_course_id))
            course = session.get(Course, cid)
            if course:
                course.grading_scale = scale_name
                session.add(course)
                session.commit()
                sess["flash_message"] = f"Grading scale for '{course.name}' updated to '{scale_name}'."
        except Exception:
            pass
    return RedirectResponse(url="/settings", status_code=303)

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
