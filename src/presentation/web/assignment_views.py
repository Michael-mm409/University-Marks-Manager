from fastapi import Form, Request
import logging
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlmodel import Session, select
from src.infrastructure.db.models import Assignment, ExamSettings, Examination, GradeType, Subject
from src.presentation.api.deps import get_session

assignment_router = APIRouter()
logger = logging.getLogger(__name__)

@assignment_router.api_route("/assignment/create", methods=["POST"], response_class=HTMLResponse)
def create_assignment(
    semester: str,
    code: str,
    year: str = Form(...),
    assessment: str = Form(...),
    weighted_mark: Optional[float] = Form(None),
    mark_weight: Optional[float] = Form(None),
    grade_type: str = Form("numeric"),
    total_mark: Optional[str] = Form(""),  # propagate desired final total to trigger recompute
    session: Session = Depends(get_session),  # noqa: B008 - FastAPI dependency injection is intended here
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
            if weighted_mark is not None:
                weighted_val = float(weighted_mark)
            if mark_weight is not None:
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
        # Persist numeric weighted marks as floats; S/U is tracked via grade_type.
        weighted_mark=(weighted_val if (grade_type == GradeType.NUMERIC.value and weighted_val is not None) else None),
        unweighted_mark=unweighted_val,
        mark_weight=mark_weight_val,
        grade_type=grade_type,
    )
    session.add(new_assignment)
    session.commit()

    # If total_mark is not provided or is empty, use the subject's stored total_mark
    if total_mark in (None, ""):
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
            goal = float(str(target_val))
        except ValueError:
            goal = None
        if goal is not None and 0 < goal <= 100:
            # Recompute assignment aggregates including newly added assignment
            assignments = session.exec(
                select(Assignment).where(
                    Assignment.semester_name == semester,
                    Assignment.year == year,
                    Assignment.subject_code == code,
                ).order_by(Assignment.assessment)
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


@assignment_router.api_route("/assignment/{assessment}/{year}/delete", methods=["POST"], response_class=HTMLResponse)
def delete_assignment(
    assessment: str,
    code: str,
    semester: str,
    year: str,
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
    existing = session.exec(
        select(Assignment).where(
            Assignment.assessment == assessment,
            Assignment.subject_code == code,
            Assignment.semester_name == semester,
            Assignment.year == year,
        )
    ).first()
    if existing:
        session.delete(existing)
        session.commit()
    return RedirectResponse(
        f"/semester/{semester}/subject/{code}?year={year}", status_code=303
    )

# AJAX endpoint: return assignment edit form HTML
@assignment_router.api_route("/assignment/{assessment}/{year}/edit", response_class=HTMLResponse, methods=["GET", "HEAD"])
def edit_assignment_form(
    request: Request,
    assessment: str,
    year: str,
    code: str,
    semester: str,
    session: Session = Depends(get_session),
):
    """
    Short description.

    Args:
        request: Description.
        assessment: Description.
        year: Description.
        code: Description.
        semester: Description.
        session: Description.

    Raises:
        Description.
    """
    assignment = session.exec(
        select(Assignment).where(
            Assignment.assessment == assessment,
            Assignment.subject_code == code,
            Assignment.semester_name == semester,
            Assignment.year == year,
        )
    ).first()
    if not assignment:
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
        <button type='button' class='btn btn-xs btn-primary' onclick="window.submitInlineEditAssignmentRow('{assessment}', '{code}', '{semester}', '{year}')">Save</button>
        <button type='button' class='btn btn-xs' onclick='window.cancelInlineEditAssignment()'>Cancel</button>
    </td>
    """)
# AJAX endpoint: update assignment and return JSON result
@assignment_router.api_route("/assignment/{assessment}/{year}/update", methods=["POST"], response_class=JSONResponse)
def update_assignment_ajax(
    assessment: str,
    code: str,
    semester: str,
    year: str,
    weighted_mark: Optional[float] = Form(None),
    mark_weight: Optional[float] = Form(None),
    grade_type: str = Form("numeric"),
    session: Session = Depends(get_session),
):
    """
    Short description.

    Args:
        assessment: Description.
        code: Description.
        semester: Description.
        year: Description.
        weighted_mark: Description.
        mark_weight: Description.
        grade_type: Description.
        session: Description.

    Raises:
        Description.
    """
    try:
        assignment = session.exec(
            select(Assignment).where(
                Assignment.assessment == assessment,
                Assignment.subject_code == code,
                Assignment.semester_name == semester,
                Assignment.year == year,
            )
        ).first()
        if not assignment:
            return JSONResponse({"success": False, "error": "Assignment not found."}, status_code=404)
        # Update fields
        if grade_type == GradeType.NUMERIC.value:
            try:
                if weighted_mark not in (None, ""):
                    weighted_val = float(weighted_mark)
                    # store numeric weighted marks as floats
                    assignment.weighted_mark = weighted_val
                else:
                    weighted_val = float(assignment.weighted_mark) if assignment.weighted_mark is not None else 0.0
                if mark_weight not in (None, ""):
                    mark_weight_val = float(mark_weight)
                    assignment.mark_weight = mark_weight_val
                else:
                    mark_weight_val = float(assignment.mark_weight) if assignment.mark_weight is not None else 0.0
                assignment.unweighted_mark = round(weighted_val / mark_weight_val, 4) if mark_weight_val else None
            except ValueError:
                return JSONResponse({"success": False, "error": "Invalid numeric values."}, status_code=400)
        elif grade_type in (GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value):
            assignment.weighted_mark = None
            assignment.mark_weight = None
            assignment.unweighted_mark = None
        assignment.grade_type = grade_type
        session.commit()
        # Recalculate and update subject total_mark after assignment edit
        subject = session.exec(
            select(Subject).where(
                Subject.subject_code == code,
                Subject.semester_name == semester,
                Subject.year == year,
            )
        ).first()
        if subject:
            assignments = session.exec(
                select(Assignment).where(
                    Assignment.subject_code == code,
                    Assignment.semester_name == semester,
                    Assignment.year == year,
                ).order_by(Assignment.assessment)
            ).all()
            exams = session.exec(
                select(Examination).where(
                    Examination.subject_code == code,
                    Examination.semester_name == semester,
                    Examination.year == year,
                )
            ).all()
            assess_weight_sum = 0.0
            assess_weighted_total = 0.0
            for a in assignments:
                if a.grade_type == GradeType.NUMERIC.value and a.mark_weight and a.weighted_mark:
                    try:
                        assess_weight_sum += float(a.mark_weight)
                        assess_weighted_total += float(a.weighted_mark)
                    except ValueError:
                        pass
            exam_mark = None
            exam_weight = None
            if exams:
                exam = exams[0]
                try:
                    exam_mark = float(exam.exam_mark)
                except (TypeError, ValueError):
                    exam_mark = None
                try:
                    exam_weight = float(exam.exam_weight)
                except (TypeError, ValueError):
                    exam_weight = None
                # Recalculate totals for display only — do NOT persist subject.total_mark here.
                total_mark = None
                if assess_weight_sum or exam_weight:
                    try:
                        total_weighted = assess_weighted_total
                        total_weight_percent = assess_weight_sum
                        if exam_mark is not None and exam_weight is not None:
                            total_weighted += (exam_mark / 100.0) * exam_weight
                            total_weight_percent += exam_weight
                        if total_weight_percent > 0:
                            total_mark = round((total_weighted / total_weight_percent) * 100.0, 2)
                    except ZeroDivisionError:
                        total_mark = None
        # Return updated row HTML for table
        row_html = (
            f"<td class='assignment-assessment'>{assignment.assessment}</td>"
            f"<td class='assignment-weighted'>{'-' if assignment.grade_type in ['S','U'] else ('%.2f' % float(assignment.weighted_mark) if assignment.weighted_mark is not None else '0.00')}</td>"
            f"<td class='assignment-unweighted'>{'-' if assignment.grade_type in ['S','U'] else ('%.2f' % float(assignment.unweighted_mark) if assignment.unweighted_mark is not None else '0.00')}</td>"
            f"<td class='assignment-mark-weight'>{'-' if assignment.grade_type in ['S','U'] else ('%.2f' % float(assignment.mark_weight) if assignment.mark_weight is not None else '0.00')}</td>"
            f"<td class='assignment-grade-type'>{assignment.grade_type}</td>"
            f"<td class='flex gap-1'>"
            f"<form method='post' action='/semester/{semester}/subject/{code}/assignment/{assessment}/{code}/{semester}/{year}/delete'>"
            f"<input type='hidden' name='year' value='{year}' />"
            f"<button class='btn btn-xs btn-error' type='submit'>✕</button>"
            f"</form>"
            f"<button class='btn btn-xs btn-outline' type='button' onclick=\"window.startInlineEditAssignment('{assessment}','{code}','{semester}','{year}')\">Edit</button>"
            f"</td>"
        )
        return JSONResponse({"success": True, "row_html": row_html})
    except Exception:
        logger.exception("update_assignment_ajax failed")
        return JSONResponse({"success": False, "error": "Internal server error"}, status_code=500)
