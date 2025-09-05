"""HTML view routes rendering Jinja templates (spaces only)."""
from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from src.presentation.api.deps import get_session
from src.infrastructure.db.models import (
    Semester,
    Subject,
    Assignment,
    Examination,
    ExamSettings,
    GradeType,
)

views = APIRouter()


def _render(request: Request, template: str, context: dict) -> HTMLResponse:
    """
    Helper to render a template with context.

    Args:
        request (Request): The incoming HTTP request.
        template (str): Template filename.
        context (dict): Context variables for the template.

    Returns:
        HTMLResponse: Rendered HTML response.
    """
    env = request.app.state.jinja_env
    tpl = env.get_template(template)
    return HTMLResponse(tpl.render(**context))


@views.get("/", response_class=HTMLResponse)
def home(request: Request, year: Optional[str] = None, session: Session = Depends(get_session)) -> HTMLResponse:
    """Home with optional year filter."""
    query = select(Semester)
    if year:
        query = query.where(Semester.year == year)
    semesters = session.exec(query).all()
    # Distinct years for filter dropdown
    years: List[str] = sorted({s.year for s in session.exec(select(Semester)).all()})
    return _render(request, "index.html", {"semesters": semesters, "years": years, "selected_year": year})


@views.post("/semester/create")
def create_semester(
    name: str = Form(...),
    year: str = Form(...),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """
    Create a new semester if it does not already exist.
    
    Args:
        name (str): Semester name.
        year (str): Semester year.
        session (Session): Database session dependency.
    
    Returns:
        RedirectResponse: Redirect to home page.
    """

    exists = session.exec(
        select(Semester).where(Semester.name == name, Semester.year == year)
    ).first()
    if not exists:
        session.add(Semester(name=name, year=year))
        session.commit()
    return RedirectResponse("/", status_code=303)


@views.post("/semester/{semester}/delete")
def delete_semester(semester: str, year: str = Form(...), session: Session = Depends(get_session)):
    """Delete a semester and all related data."""
    # Delete assignments, exams, settings, subjects for that semester/year
    subs = session.exec(select(Subject).where(Subject.semester_name == semester, Subject.year == year)).all()
    for sub in subs:
        session.exec(
            select(Assignment).where(
                Assignment.semester_name == semester,
                Assignment.year == year,
                Assignment.subject_code == sub.subject_code,
            )
        )  # placeholder retrieval (deletion with ORM objects below)
    # Direct delete via ORM load (simpler for small dataset)
    assignments = session.exec(select(Assignment).where(Assignment.semester_name == semester, Assignment.year == year)).all()
    exams = session.exec(select(Examination).where(Examination.semester_name == semester, Examination.year == year)).all()
    settings = session.exec(select(ExamSettings).where(ExamSettings.semester_name == semester, ExamSettings.year == year)).all()
    # Delete each collection explicitly (avoids type checker complaints about '+' on heterogeneous sequences)
    for obj in assignments:
        session.delete(obj)
    for obj in exams:
        session.delete(obj)
    for obj in settings:
        session.delete(obj)
    for obj in subs:
        session.delete(obj)
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == year)).first()
    if sem:
        session.delete(sem)
    session.commit()
    return RedirectResponse("/", status_code=303)


@views.post("/semester/{semester}/update")
def update_semester(semester: str, year: str = Form(...), new_name: str = Form(...), session: Session = Depends(get_session)):
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == year)).first()
    if sem:
        sem.name = new_name
        session.commit()
    return RedirectResponse("/", status_code=303)


@views.get("/semester/{semester}", response_class=HTMLResponse)
def semester_detail(
    request: Request,
    semester: str,
    year: str,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    """
    Render the semester detail page listing subjects in the semester/year with summary metrics.
    
    Args:
        request (Request): The incoming HTTP request.
        semester (str): Semester name.
        year (str): Semester year.
        session (Session): Database session dependency.
    
    Returns:
        HTMLResponse: Rendered semester detail page.
    """
    subjects = session.exec(
        select(Subject).where(Subject.semester_name == semester, Subject.year == year)
    ).all()
    # Build summary rows similar to provided screenshot
    summaries = []
    for sub in subjects:
        assignments = session.exec(
            select(Assignment).where(
                Assignment.semester_name == semester,
                Assignment.year == year,
                Assignment.subject_code == sub.subject_code,
            )
        ).all()
        exam = session.exec(
            select(Examination).where(
                Examination.semester_name == semester,
                Examination.year == year,
                Examination.subject_code == sub.subject_code,
            )
        ).first()
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
        if exam:
            try:
                exam_mark = float(exam.exam_mark)
            except (TypeError, ValueError):
                exam_mark = None
            try:
                exam_weight = float(exam.exam_weight)
            except (TypeError, ValueError):
                exam_weight = None
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
        summaries.append(
            {
                "code": sub.subject_code,
                "name": sub.subject_name,
                "assessment_mark": round(assess_weighted_total, 2),
                "assessment_weight": assess_weight_sum,
                "exam_mark": exam_mark,
                "exam_weight": exam_weight,
                "total_mark": total_mark,
                "sync_subject": sub.sync_subject,
            }
        )
    return _render(
        request,
        "semester.html",
        {"semester": semester, "year": year, "subjects": subjects, "subject_summaries": summaries},
    )


@views.post("/semester/{semester}/subject/create")
def create_subject(
    semester: str,
    year: str = Form(...),
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    sync_subject: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """
    Create a new subject in the semester if it does not already exist.
    
    Args:
        semester (str): Semester name.
        year (str): Semester year.
        subject_code (str): Subject code.
        subject_name (str): Subject name.
        sync_subject (Optional[str]): Sync subject identifier.
        session (Session): Database session dependency.
        
    Returns:
        RedirectResponse: Redirect to semester detail page.
    """
    exists = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == subject_code,
        )
    ).first()
    if not exists:
        session.add(
            Subject(
                subject_code=subject_code,
                subject_name=subject_name,
                semester_name=semester,
                year=year,
                sync_subject=bool(sync_subject),
            )
        )
        session.commit()
    return RedirectResponse(f"/semester/{semester}?year={year}", status_code=303)


@views.api_route("/semester/{semester}/subject/{code}", methods=["GET"], response_class=HTMLResponse)
def subject_detail(
    request: Request,
    semester: str,
    code: str,
    year: str,
    exam_weight: Optional[float] = None,
    final_total: Optional[float] = None,
    total_mark: Optional[float] = None,
    session: Session = Depends(get_session),
):
    """Render the subject detail page showing assignments, exams, and computed averages."""
    subject = session.exec(
        select(Subject).where(
            Subject.semester_name == semester,
            Subject.year == year,
            Subject.subject_code == code,
        )
    ).first()
    if not subject:
        return HTMLResponse("Subject not found", status_code=404)

    assignments = session.exec(
        select(Assignment).where(
            Assignment.semester_name == semester,
            Assignment.year == year,
            Assignment.subject_code == code,
        )
    ).all()
    examinations = session.exec(
        select(Examination).where(
            Examination.semester_name == semester,
            Examination.year == year,
            Examination.subject_code == code,
        )
    ).all()

    assignment_weighted_sum = 0.0
    assignment_weight_percent = 0.0
    for a in assignments:
        if a.grade_type == GradeType.NUMERIC.value and a.weighted_mark and a.mark_weight:
            try:
                assignment_weighted_sum += float(a.weighted_mark)
                assignment_weight_percent += float(a.mark_weight)
            except ValueError:
                pass

    exam_raw_percent: Optional[float] = None
    exam_contribution = 0.0
    existing_exam_weight = 0.0
    single_exam = examinations[0] if examinations else None
    if single_exam:
        try:
            exam_raw_percent = float(single_exam.exam_mark)
        except (TypeError, ValueError):
            exam_raw_percent = None
        try:
            existing_exam_weight = float(single_exam.exam_weight)
        except (TypeError, ValueError):
            existing_exam_weight = 0.0

    inferred_remaining = 0.0
    if not examinations:
        inferred_remaining = max(0.0, 100.0 - assignment_weight_percent)

    # Determine which exam weight to use for requirement calculations
    effective_exam_weight = (
        existing_exam_weight
        or (exam_weight if (exam_weight and not examinations) else inferred_remaining)
    )
    # PS exam scaling: user-defined factor (default 40%), expressed as percentage of exam weight contributing
    # Load persisted PS settings
    setting = session.exec(
        select(ExamSettings).where(
            ExamSettings.semester_name == semester,
            ExamSettings.year == year,
            ExamSettings.subject_code == code,
        )
    ).first()
    ps_exam = bool(setting.ps_exam) if setting else False
    parsed_factor = setting.ps_factor if setting else 40.0
    scaling = (parsed_factor / 100.0) if ps_exam else 1.0
    effective_scoring_exam_weight = effective_exam_weight * scaling

    if exam_raw_percent is not None and effective_scoring_exam_weight > 0:
        exam_contribution = (exam_raw_percent / 100.0) * effective_scoring_exam_weight

    total_weighted = assignment_weighted_sum + exam_contribution
    total_scoring_weight_percent = assignment_weight_percent + (
        effective_scoring_exam_weight if effective_scoring_exam_weight else 0.0
    )
    average = (
        round(total_weighted / total_scoring_weight_percent * 100, 2)
        if total_scoring_weight_percent
        else None
    )

    required_exam_mark: Optional[float] = None
    requirement_status: Optional[str] = None
    projected_total_weighted: Optional[float] = None

    # Allow user to pass either final_total (desired final percentage) or total_mark (alias)
    desired_goal = final_total if final_total is not None else total_mark
    if desired_goal is not None:
        try:
            goal = float(desired_goal)
            if goal <= 0 or goal > 100:
                requirement_status = "invalid"
            else:
                # If we already have an exam mark and achieved goal
                if average is not None and exam_raw_percent is not None and average >= goal:
                    requirement_status = "achieved"
                else:
                    effective_exam_score = effective_scoring_exam_weight
                    if effective_exam_score <= 0:
                        requirement_status = "impossible"
                    else:
                        # Equation: (assign_sum + exam_required/100 * effective_exam_score) / (total_assignment_weight + effective_exam_score) * 100 = goal
                        required_exam_mark = (
                            (goal / 100.0) * (assignment_weight_percent + effective_exam_score) - assignment_weighted_sum
                        ) * 100.0 / effective_exam_score
                        if required_exam_mark < 0:
                            requirement_status = "achieved"
                        elif required_exam_mark > 100:
                            requirement_status = "impossible"
                        else:
                            requirement_status = "feasible"
                        if requirement_status in ("feasible", "achieved"):
                            projected_total_weighted = round(goal, 2)
        except ValueError:
            requirement_status = "invalid"

    return _render(
        request,
        "subject.html",
        {
            "semester": semester,
            "year": year,
            "subject": subject,
            "assignments": assignments,
            "examinations": examinations,
            "total_weighted": round(total_weighted, 2),
            "projected_total_weighted": projected_total_weighted,
            "total_weight_percent": round(total_scoring_weight_percent, 2),
            "average": average,
            "final_total": desired_goal,
            "total_mark": desired_goal,
            "effective_exam_weight": effective_exam_weight,
            "required_exam_mark": None if required_exam_mark is None
                 else round(required_exam_mark, 2),
            "requirement_status": requirement_status,
            "ps_exam": ps_exam,
            "ps_factor": parsed_factor if ps_exam else None,
            "raw_exam_percent": exam_raw_percent,
            "assignment_weighted_sum": round(assignment_weighted_sum, 2),
            "assignment_weight_percent": round(assignment_weight_percent, 2),
            "exam_weighted_sum": round(exam_contribution, 2),
            "effective_scoring_exam_weight": round(effective_scoring_exam_weight, 2),
        },
    )


@views.post("/semester/{semester}/subject/{code}/assignment/create")
def create_assignment(
    semester: str,
    code: str,
    year: str = Form(...),
    assessment: str = Form(...),
    weighted_mark: Optional[str] = Form(""),
    mark_weight: Optional[str] = Form(""),
    grade_type: str = Form("numeric"),
    total_mark: Optional[str] = Form(None),  # propagate desired final total to trigger recompute
    final_total: Optional[str] = Form(None),  # legacy field
    session: Session = Depends(get_session),
) -> RedirectResponse:
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
    if grade_type == GradeType.NUMERIC.value and weighted_mark and mark_weight:
        try:
            weighted_val = float(weighted_mark)
            mark_weight_val = float(mark_weight)
            if mark_weight_val:
                unweighted_val = round(weighted_val / mark_weight_val, 4)
        except ValueError:
            pass
    if grade_type in (GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value):
        weighted_val = grade_type
        mark_weight_val = None
        unweighted_val = None
    new_assignment = Assignment(
        subject_code=code,
        semester_name=semester,
        year=year,
        assessment=assessment,
        weighted_mark=str(weighted_val) if weighted_val is not None else None,
        unweighted_mark=unweighted_val,
        mark_weight=mark_weight_val,
        grade_type=grade_type,
    )
    session.add(new_assignment)
    session.commit()

    # If a desired total mark target exists, recompute (or create) exam record with derived needed exam mark.
    target_val = total_mark or final_total
    if target_val:
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


@views.post("/semester/{semester}/subject/{code}/assignment/{assignment_id}/delete")
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


@views.post("/semester/{semester}/subject/{code}/totalMark/save")
def save_total_mark(
    semester: str,
    code: str,
    year: str = Form(...),
    total_mark: Optional[str] = Form(""),  # desired total final percentage
    exam_mark: Optional[str] = Form(""),   # fallback legacy field
    ps_exam: Optional[str] = Form(None),
    ps_factor: Optional[str] = Form(None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Create or update exam using desired total mark input.

    If user supplies a desired overall final percentage (total_mark), derive the
    implied exam mark needed given current assignment contributions and exam weight.
    If exam_mark provided explicitly (legacy), that value is stored instead.
    """
    # Fetch existing exam (single allowed)
    existing = session.exec(
        select(Examination).where(
            Examination.semester_name == semester,
            Examination.year == year,
            Examination.subject_code == code,
        )
    ).first()

    # Aggregate assignment weighted marks and weight percent
    assignments = session.exec(
        select(Assignment).where(
            Assignment.semester_name == semester,
            Assignment.year == year,
            Assignment.subject_code == code,
        )
    ).all()
    assignment_weight_percent = 0.0
    assignment_weighted_sum = 0.0
    for a in assignments:
        if a.grade_type == GradeType.NUMERIC.value and a.mark_weight and a.weighted_mark:
            try:
                assignment_weight_percent += float(a.mark_weight)
                assignment_weighted_sum += float(a.weighted_mark)
            except ValueError:
                pass

    # Determine exam weight (existing or inferred remaining)
    current_exam_weight = existing.exam_weight if existing else 0.0
    if not current_exam_weight:
        current_exam_weight = max(0.0, 100.0 - assignment_weight_percent)

    derived_exam_mark: float = 0.0

    if total_mark:
        try:
            goal = float(total_mark)
        except ValueError:
            goal = None
        # Determine effective scoring weight with PS scaling if requested
        ps_enabled = bool(ps_exam)
        scaling = 1.0
        if ps_enabled:
            try:
                scaling = (float(ps_factor) if ps_factor else 40.0) / 100.0
            except ValueError:
                scaling = 0.4
        # Persist/retrieve settings
        setting = session.exec(
            select(ExamSettings).where(
                ExamSettings.semester_name == semester,
                ExamSettings.year == year,
                ExamSettings.subject_code == code,
            )
        ).first()
        ps_enabled = bool(ps_exam)
        factor_val = 40.0
        if ps_factor:
            try:
                factor_val = float(ps_factor)
            except ValueError:
                factor_val = 40.0
        if not setting:
            setting = ExamSettings(
                subject_code=code,
                semester_name=semester,
                year=year,
                ps_exam=ps_enabled,
                ps_factor=factor_val,
            )
            session.add(setting)
        else:
            setting.ps_exam = ps_enabled
            setting.ps_factor = factor_val
        scaling = (factor_val / 100.0) if ps_enabled else 1.0
        scoring_weight = current_exam_weight * scaling if ps_enabled else current_exam_weight
        if goal is not None and 0 < goal <= 100 and scoring_weight > 0:
            needed_exam = (
                (goal / 100.0) * (assignment_weight_percent + scoring_weight) - assignment_weighted_sum
            ) * 100.0 / scoring_weight
            if needed_exam < 0:
                needed_exam = 0.0
            if needed_exam > 100:
                needed_exam = 100.0  # cap; UI can show impossible if desired
            derived_exam_mark = round(needed_exam, 4)
    # Legacy direct exam_mark override if provided and numeric
    if exam_mark:
        try:
            derived_exam_mark = float(exam_mark)
        except ValueError:
            pass

    if existing:
        existing.exam_mark = derived_exam_mark
        if not existing.exam_weight:
            existing.exam_weight = current_exam_weight
    else:
        new_exam = Examination(
            subject_code=code,
            semester_name=semester,
            year=year,
            exam_mark=derived_exam_mark,
            exam_weight=current_exam_weight,
        )
        session.add(new_exam)
    session.commit()
    # Redirect without legacy ps_exam query params; state now persisted
    return RedirectResponse(
        f"/semester/{semester}/subject/{code}?year={year}&total_mark={total_mark}", status_code=303
    )


@views.post("/semester/{semester}/subject/{code}/exam/{exam_id}/delete")
def delete_exam(
    semester: str,
    code: str,
    exam_id: int,
    year: str = Form(...),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Delete the examination record for a subject (single exam model)."""
    existing = session.get(Examination, exam_id)
    if existing and existing.subject_code == code and existing.semester_name == semester and existing.year == year:
        session.delete(existing)
        session.commit()
    return RedirectResponse(
        f"/semester/{semester}/subject/{code}?year={year}", status_code=303
    )

__all__ = ["views"]
