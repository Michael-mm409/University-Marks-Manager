from fastapi import Form, Request
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlmodel import Session, select
from src.infrastructure.db.models import Assignment, ExamSettings, Examination, GradeType, Subject
from src.presentation.api.deps import get_session

assignment_router = APIRouter()

@assignment_router.api_route("/assignment/create", methods=["POST"], response_class=HTMLResponse)
def create_assignment(
    semester: str,
    code: str,
    year: str = Form(...),
    assessment: str = Form(...),
    weighted_mark: Optional[str] = Form(""),
    mark_weight: Optional[str] = Form(""),
    grade_type: str = Form("numeric"),
    total_mark: Optional[int] = Form(0),  # propagate desired final total to trigger recompute
    session: Session = Depends(get_session),
):
    """
    Create a new assignment for the subject.
    
    Args:
        semester (str): Semester name.
        code (str): Subject code.
        year (str): Semester year.
        assessment (str): Assignment name/description.
        weighted_mark (Optional[str]): Weighted mark as string.
        mark_weight (Optional[str]): Mark weight as string.
        grade_type (str): Grade type ("numeric", "satisfactory", "unsatisfactory").
        session (Session): Database session dependency.
    
    Raises:
        ValueError: If numeric values are invalid.
    
    Returns:
        RedirectResponse: Redirect to subject detail page.
    """
    unweighted_val = None
    weighted_val = None
    mark_weight_val = None
    if grade_type == GradeType.NUMERIC.value:
        try:
            if weighted_mark not in (None, ""):
                weighted_val = float(weighted_mark)
            if mark_weight not in (None, ""):
                mark_weight_val = float(mark_weight)
            # Only calculate unweighted if both are provided
            if weighted_val is not None and mark_weight_val is not None and mark_weight_val:
                unweighted_val = round(weighted_val / mark_weight_val, 4)
        except ValueError:
            weighted_val = None
            mark_weight_val = None
            unweighted_val = None
    if grade_type in (GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value):
        weighted_val = None
        mark_weight_val = None
        unweighted_val = None
    existing_assignment = session.exec(
        select(Assignment).where(
            Assignment.subject_code == code,
            Assignment.semester_name == semester,
            Assignment.year == year,
            Assignment.assessment == assessment,
        )
    ).first()
    if existing_assignment:
        return HTMLResponse("An assignment with this name already exists for this subject/semester/year.", status_code=400)
    new_assignment = Assignment(
        subject_code=code,
        semester_name=semester,
        year=year,
        assessment=assessment,
        weighted_mark=weighted_val if grade_type == GradeType.NUMERIC.value else None,
        unweighted_mark=unweighted_val,
        mark_weight=mark_weight_val,
        grade_type=grade_type,
    )
    session.add(new_assignment)
    session.commit()

    # If total_mark is not provided or is empty, use the subject's stored total_mark
    if total_mark == "" or total_mark is None:
        subject = session.exec(
            select(Subject).where(
                Subject.semester_name == semester,
                Subject.year == year,
                Subject.subject_code == code,
            )
        ).first()
        target_val = subject.total_mark if subject and subject.total_mark is not None else None
    else:
        target_val = total_mark

    # Only parse and use target_val if it is not empty or None
    if target_val not in (None, ""):
        try:
            goal = float(target_val)
        except ValueError:
            goal = None
        if goal is not None and 0 < goal <= 100:
            # Recompute assignment aggregates including newly added assignment
            assignments = session.exec(
                select(Assignment).where(
                    Assignment.semester_name == semester,
                    Assignment.year == year,
                    Assignment.subject_code == code,
                )
            ).all()
            assign_weight_sum = 0.0
            assign_weighted_total = 0.0
            for a in assignments:
                if a.grade_type == GradeType.NUMERIC.value and a.mark_weight and a.weighted_mark:
                    try:
                        assign_weight_sum += float(a.mark_weight)
                        assign_weighted_total += float(a.weighted_mark)
                    except ValueError:
                        pass
            existing_exam = session.exec(
                select(Examination).where(
                    Examination.semester_name == semester,
                    Examination.year == year,
                    Examination.subject_code == code,
                )
            ).first()
            exam_weight = existing_exam.exam_weight if existing_exam else max(0.0, 100.0 - assign_weight_sum)
            # Apply PS scaling based on persisted settings (if any)
            setting = session.exec(
                select(ExamSettings).where(
                    ExamSettings.semester_name == semester,
                    ExamSettings.year == year,
                    ExamSettings.subject_code == code,
                )
            ).first()
            ps_enabled = bool(setting.ps_exam) if setting else False
            factor_val = setting.ps_factor if (setting and setting.ps_factor) else 40.0
            scaling = (factor_val / 100.0) if ps_enabled else 1.0
            effective_exam_weight = exam_weight * scaling
            if effective_exam_weight > 0:
                needed_exam = (
                    (goal / 100.0) * (assign_weight_sum + effective_exam_weight) - assign_weighted_total
                ) * 100.0 / effective_exam_weight
                if needed_exam < 0:
                    needed_exam = 0.0
                if needed_exam > 100:
                    needed_exam = 100.0
                if existing_exam:
                    existing_exam.exam_mark = round(needed_exam, 4)
                else:
                    session.add(
                        Examination(
                            subject_code=code,
                            semester_name=semester,
                            year=year,
                            exam_mark=round(needed_exam, 4),
                            exam_weight=exam_weight,  # store original weight; scaling is conceptual
                        )
                    )
                session.commit()
    return RedirectResponse(
        f"/semester/{semester}/subject/{code}?year={year}&total_mark={target_val or ''}", status_code=303
    )


@assignment_router.api_route("/assignment/{assignment_id}/delete", methods=["POST"], response_class=HTMLResponse)
def delete_assignment(
    semester: str,
    code: str,
    assignment_id: int,
    year: str = Form(...),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """
    Delete an assignment by ID.
    
    Args:
        semester (str): Semester name.
        code (str): Subject code.
        assignment_id (int): ID of the assignment to delete.
        year (str): Semester year.
        session (Session): Database session dependency.
    
    Returns:
        RedirectResponse: Redirect to subject detail page.
    """
    existing = session.get(Assignment, assignment_id)
    if (
        existing
        and existing.subject_code == code
        and existing.semester_name == semester
        and existing.year == year
    ):
        session.delete(existing)
        session.commit()
    return RedirectResponse(
        f"/semester/{semester}/subject/{code}?year={year}", status_code=303
    )

# AJAX endpoint: return assignment edit form HTML
@assignment_router.api_route("/assignment/{assignment_id}/edit", response_class=HTMLResponse, methods=["GET", "HEAD"])
def edit_assignment_form(
    request: Request,
    semester: str,
    code: str,
    assignment_id: int,
    year: str,
    session: Session = Depends(get_session),
):
        assignment = session.get(Assignment, assignment_id)
        if not assignment or assignment.subject_code != code or assignment.semester_name != semester or assignment.year != year:
                return HTMLResponse("Assignment not found", status_code=404)
        # Return only <td> cells for inline editing, with a form inside the last cell
        return HTMLResponse(f"""
    <td><input name='assessment' class='input input-xs w-24' value='{assignment.assessment}' required /></td>
    <td><input name='weighted_mark' type='number' step='any' min='0' class='input input-xs w-16' value='{assignment.weighted_mark if assignment.weighted_mark is not None else ''}' placeholder='Weighted mark' /></td>
    <td class='assignment-unweighted'><input name='unweighted_mark' type='text' class='input input-xs w-16' value="{'-' if assignment.grade_type in ['S','U'] else ('%.2f' % float(assignment.unweighted_mark) if assignment.unweighted_mark is not None else '0.00')}" readonly /></td>
    <td><input name='mark_weight' type='number' step='any' min='0' class='input input-xs w-16' value='{assignment.mark_weight if assignment.mark_weight is not None else ''}' placeholder='Mark weight' /></td>
    <td><select name='grade_type' class='select select-xs w-16'>
            <option value='numeric' {'selected' if assignment.grade_type == 'numeric' else ''}>Numeric</option>
            <option value='S' {'selected' if assignment.grade_type == 'S' else ''}>S</option>
            <option value='U' {'selected' if assignment.grade_type == 'U' else ''}>U</option>
        </select></td>
    <td class='flex gap-1'>
        <button type='button' class='btn btn-xs btn-primary' onclick="submitInlineEditAssignmentRow('{assignment_id}', '{year}')">Save</button>
        <button type='button' class='btn btn-xs' onclick='cancelInlineEditAssignment()'>Cancel</button>
    </td>
    """)
# AJAX endpoint: update assignment and return JSON result
@assignment_router.api_route("/assignment/{assignment_id}/update", methods=["POST"], response_class=JSONResponse)
def update_assignment_ajax(
    semester: str,
    code: str,
    assignment_id: int,
    year: str = Form(...),
    assessment: str = Form(...),
    weighted_mark: Optional[str] = Form(""),
    mark_weight: Optional[str] = Form(""),
    grade_type: str = Form("numeric"),
    session: Session = Depends(get_session),
):
    try:
        assignment = session.get(Assignment, assignment_id)
        if not assignment or assignment.subject_code != code or assignment.semester_name != semester or assignment.year != year:
            return JSONResponse({"success": False, "error": "Assignment not found."}, status_code=404)
        # Check for duplicate assessment name (excluding self)
        duplicate = session.exec(
            select(Assignment).where(
                Assignment.subject_code == code,
                Assignment.semester_name == semester,
                Assignment.year == year,
                Assignment.assessment == assessment,
                Assignment.id != assignment_id,
            )
        ).first()
        if duplicate:
            return JSONResponse({"success": False, "error": "Another assignment with this name exists."}, status_code=400)
        # Update fields
        assignment.assessment = assessment
        if grade_type == GradeType.NUMERIC.value:
            # Update weighted_mark independently
            try:
                if weighted_mark not in (None, ""):
                    weighted_val = float(weighted_mark)
                    assignment.weighted_mark = weighted_val
                else:
                    weighted_val = assignment.weighted_mark if assignment.weighted_mark is not None else 0.0
                if mark_weight not in (None, ""):
                    mark_weight_val = float(mark_weight)
                    assignment.mark_weight = mark_weight_val
                else:
                    mark_weight_val = assignment.mark_weight if assignment.mark_weight is not None else 0.0
                assignment.unweighted_mark = round(weighted_val / mark_weight_val, 4) if mark_weight_val else None
            except ValueError:
                return JSONResponse({"success": False, "error": "Invalid numeric values."}, status_code=400)
        elif grade_type in (GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value):
            assignment.weighted_mark = None
            assignment.mark_weight = None
            assignment.unweighted_mark = None
        assignment.grade_type = grade_type
        session.commit()
        # Return updated row HTML for table
        row_html = (
            f"<td class='assignment-assessment'>{assignment.assessment}</td>"
            f"<td class='assignment-weighted'>{'-' if assignment.grade_type in ['S','U'] else ('%.2f' % float(assignment.weighted_mark) if assignment.weighted_mark is not None else '0.00')}</td>"
            f"<td class='assignment-unweighted'>{'-' if assignment.grade_type in ['S','U'] else ('%.2f' % float(assignment.unweighted_mark) if assignment.unweighted_mark is not None else '0.00')}</td>"
            f"<td class='assignment-mark-weight'>{'-' if assignment.grade_type in ['S','U'] else ('%.2f' % float(assignment.mark_weight) if assignment.mark_weight is not None else '0.00')}</td>"
            f"<td class='assignment-grade-type'>{assignment.grade_type}</td>"
            f"<td class='flex gap-1'>"
            f"<form method='post' action='/semester/{semester}/subject/{code}/assignment/{assignment_id}/delete'>"
            f"<input type='hidden' name='year' value='{year}' />"
            f"<button class='btn btn-xs btn-error' type='submit'>✕</button>"
            f"</form>"
            f"<button class='btn btn-xs btn-outline' type='button' onclick=\"startInlineEditAssignment('{assignment_id}')\">Edit</button>"
            f"</td>"
        )
        return JSONResponse({"success": True, "row_html": row_html})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return JSONResponse({"success": False, "error": f"Server error: {str(e)}\n{tb}"}, status_code=500)
