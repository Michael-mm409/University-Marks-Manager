from fastapi import Depends, Form, Request, APIRouter, Response
from typing import List, cast
from fastapi.responses import RedirectResponse
from sqlmodel import Session, col, select
from sqlalchemy import Table
from src.presentation.api.deps import get_session
from src.infrastructure.db.models import Semester, Subject, Assignment, Examination, ExamSettings, GradeType
from .template_helpers import _render
from src.core.services.semester_manager import SemesterManager
from src.core.services.course_manager import CourseManager
semester_router = APIRouter()
from .types import SemesterSummary, SemesterContext

@semester_router.api_route("/create", methods=["POST"])
def create_semester(
    request: Request,
    name: str = Form(...),
    year: str = Form(...),
    return_year: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> Response:
    """
    Create a new semester if it does not already exist.
    
    Args:
        name (str): Semester name.
        year (str): Semester year.
        session (Session): Database session dependency.
    
    Returns:
        RedirectResponse: Redirect to home page.
    """
    env = request.app.state.jinja_env
    # Validate: year must be an integer within a sensible range
    year_str = str(year).strip()
    year_int: int | None = None
    try:
        year_int = int(year_str)
    except Exception:
        year_int = None

    def _render_add_card(error: str | None = None) -> Response:
        html = env.get_template("partials/add_semester_card.html").render(
            request=request,
            selected_year=return_year or year_str or request.app.state.jinja_env.globals.get("current_year"),
            current_year=request.app.state.jinja_env.globals.get("current_year"),
            form_name=name,
            form_year=year_str,
            error=error,
        )
        return Response(content=html, media_type="text/html")

    if year_int is None or year_int < 2000 or year_int > 2100:
        # HTMX: replace the card with error while preserving inputs
        if request.headers.get("HX-Request", "").lower() == "true":
            return _render_add_card("Please enter a valid numeric year between 2000 and 2100.")
        # Non-HTMX: set flash and redirect back
        try:
            request.session["flash_message"] = "Invalid year. Please enter a number between 2000 and 2100."
        except Exception:
            pass
        target_year = (return_year or year_str or "").strip()
        return RedirectResponse(f"/?year={target_year}", status_code=303)

    exists = session.exec(
        select(Semester).where(Semester.name == name, Semester.year == year_int)
    ).first()
    if not exists:
        # If a course is active, auto-link the new semester to that course
        course_id = request.session.get("current_course_id")
        try:
            cid = int(course_id) if course_id is not None else None
        except Exception:
            cid = None
        session.add(Semester(name=name, year=year_int, course_id=cid))
        session.commit()
    else:
        # If the semester exists but is unassigned, and a course is active, link it
        if getattr(exists, "course_id", None) is None:
            course_id = request.session.get("current_course_id")
            try:
                cid = int(course_id) if course_id is not None else None
            except Exception:
                cid = None
            if cid is not None:
                exists.course_id = cid
                session.commit()
    # Redirect back to the filtered year if provided; otherwise use the semester's year
    target_year = (return_year or str(year_int)).strip() if str(return_year or "").strip() else str(year_int)
    if request.headers.get("HX-Request", "").lower() == "true":
        # Return updated add card (cleared name) and swap semesters section OOB
        add_card_html = env.get_template("partials/add_semester_card.html").render(
            request=request,
            selected_year=target_year,
            current_year=request.app.state.jinja_env.globals.get("current_year"),
            form_name="",
            form_year=target_year,
            error=None,
        )
        # Render the section with oob swap enabled
        section_html = _render_semesters_section_string(request, session, target_year, oob=True)
        return Response(content=add_card_html + section_html, media_type="text/html")
    return RedirectResponse(f"/?year={target_year}", status_code=303)


@semester_router.api_route("/{semester}/delete", methods=["POST"])
def delete_semester(
    request: Request,
    semester: str,
    year: str = Form(...),
    return_year: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> Response:
    """Delete a semester and all related data."""
    # Delete assignments, exams, settings, subjects for that semester/year
    # First get the semester_id
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == int(year))).first()
    sem_id = getattr(sem, "id", None)
    subs = session.exec(select(Subject).where(Subject.semester_id == sem_id)).all() if sem_id else []
    subject_ids = [getattr(s, "id", None) for s in subs if getattr(s, "id", None) is not None]
    # Direct delete via ORM load (simpler for small dataset), prefer subject_id-based lookups
    assignments = []
    exams = []
    settings = []
    if subject_ids:
        for sid in subject_ids:
            assignments.extend(session.exec(select(Assignment).where(Assignment.subject_id == sid)).all())
            exams.extend(session.exec(select(Examination).where(Examination.subject_id == sid)).all())
            settings.extend(session.exec(select(ExamSettings).where(ExamSettings.subject_id == sid)).all())
    # Delete each collection explicitly (avoids type checker complaints about '+' on heterogeneous sequences)
    for obj in assignments:
        session.delete(obj)
    for obj in exams:
        session.delete(obj)
    for obj in settings:
        session.delete(obj)
    for obj in subs:
        session.delete(obj)
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == int(year))).first()
    if sem:
        session.delete(sem)
    session.commit()
    # Preserve selected filter year if provided
    target_year = (return_year or year).strip() if str(return_year or "").strip() else str(year)
    if request.headers.get("HX-Request", "").lower() == "true":
        return _render_semesters_grid(request, session, target_year)
    return RedirectResponse(f"/?year={target_year}", status_code=303)


@semester_router.api_route("/{semester}/update", methods=["POST"])
def update_semester(
    request: Request,
    semester: str,
    year: str = Form(...),
    new_name: str = Form(...),
    return_year: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> Response:
    """Rename a semester and preserve the current year filter on redirect.

    Redirects back to Home with ?year=<year> so the filtered view remains active.
    """
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == int(year))).first()
    if sem:
        sem.name = new_name
        session.commit()
    # Preserve the filtered year the user was viewing if provided (fallback to the semester's year)
    target_year = (return_year or year).strip() if str(return_year or "").strip() else str(year)
    if request.headers.get("HX-Request", "").lower() == "true":
        return _render_semesters_grid(request, session, target_year)
    return RedirectResponse(f"/?year={target_year}", status_code=303)


def build_semester_context(session: Session, semester: str, year: str) -> SemesterContext:
    """Build the context used by the semester detail page for rendering."""
    # Order at the database level by subject_code for predictable display
    # First resolve semester_id
    sem = session.exec(select(Semester).where(Semester.name == semester, Semester.year == int(year))).first()
    sem_id = getattr(sem, "id", None)
    subjects_table = cast(Table, getattr(Subject, "__table__"))
    # Get synced subjects: same year but different semester
    all_sems_for_year = session.exec(select(Semester).where(Semester.year == int(year))).all()
    other_sem_ids = [s.id for s in all_sems_for_year if s.id != sem_id]
    # Fetch all subjects (main + synced) in a single SQL query with ORDER BY
    from sqlalchemy import or_, false
    display_subjects = session.exec(
        select(Subject)
        .where(
            or_(
                Subject.semester_id == sem_id,
                (
                    (col(Subject.semester_id).in_(other_sem_ids)) &
                    (Subject.sync_subject == True) &
                    (Subject.semester_year == int(year))
                ) if other_sem_ids else false()
            )
        )
        .order_by(subjects_table.c.subject_code.asc())
    ).all() if sem_id else []
    summaries: List[SemesterSummary] = []
    missing_exam_subjects: List[str] = []
    import logging
    logger = logging.getLogger("uvicorn.error")
    for sub in display_subjects:
        sid = getattr(sub, "id", None)
        assignments = session.exec(
            select(Assignment).where(
                Assignment.subject_id == sid,
            ).order_by(Assignment.assessment)
        ).all()
        exam = session.exec(
            select(Examination).where(
                Examination.subject_id == sid
            )
        ).first()
        # Fetch PS Factor settings
        setting = session.exec(
            select(ExamSettings).where(
                ExamSettings.subject_id == sid
            )
        ).first()
        ps_exam = bool(setting.ps_exam) if setting else False
        ps_factor = setting.ps_factor if setting else 40.0
        scaling = (ps_factor / 100.0) if ps_exam else 1.0
        # Identify assignment-based exam
        exam_assignment = next((a for a in assignments if getattr(a, "is_exam", False)), None)

        assess_weight_sum = 0.0
        assess_weighted_total = 0.0
        assignment_weights = []
        for a in assignments:
            # Skip assignment-based exam in assessment totals
            if getattr(a, "is_exam", False):
                continue

            if a.grade_type == GradeType.NUMERIC.value:
                if a.mark_weight not in (None, ""):
                    try:
                        w = float(a.mark_weight)
                        assess_weight_sum += w
                        assignment_weights.append(w)
                    except ValueError:
                        pass
                if a.weighted_mark not in (None, ""):
                    try:
                        assess_weighted_total += float(a.weighted_mark)
                    except ValueError:
                        pass
        print(f"[SEMESTER_SUMMARY_DEBUG] Subject: {sub.subject_code} | Assignment Weights: {assignment_weights} | Sum: {assess_weight_sum}")

        # Always calculate exam_weight for summary
        total_mark = sub.total_mark if sub.total_mark not in (None, 0) else None
        
        # Check if we have an assignment-based exam (is_exam=True)
        if exam_assignment:
            # Use the assignment-based exam data
            exam_weight = float(exam_assignment.mark_weight) if exam_assignment.mark_weight not in (None, "") else None
            exam_mark = float(exam_assignment.weighted_mark) if exam_assignment.weighted_mark not in (None, "") else None
        else:
            # Fall back to Examination table
            exam_weight = exam.exam_weight if exam else None
            exam_mark = exam.exam_mark if exam else None

        # Track subjects missing both Examination and assignment-based exam
        if exam is None and exam_assignment is None:
            missing_exam_subjects.append(sub.subject_code)
        
        final_exam_mark_weight = exam_weight
        effective_scoring_exam_weight = exam_weight * scaling if exam_weight is not None else None
        is_exam_required = False
        # Debug logging for exam_weight
        logger.info(f"[DEBUG] Subject: {sub.subject_code} | Exam Weight: {exam_weight} | Exam Mark: {exam_mark} | Assessment Weight: {assess_weight_sum} | Assessment Mark: {assess_weighted_total}")

        summaries.append(
            {
                "code": sub.subject_code,
                "name": sub.subject_name,
                "semester_name": semester,
                "credit_points": getattr(sub, "credit_points", None),
                "assessment_mark": round(assess_weighted_total, 2),
                "assessment_weight": assess_weight_sum,
                "exam_mark": exam_mark,
                "exam_weight": exam_weight,
                "final_exam_mark_weight": final_exam_mark_weight,
                "effective_scoring_exam_weight": effective_scoring_exam_weight,
                "ps_exam": ps_exam,
                "ps_factor": ps_factor,
                "total_mark": total_mark,
                "sync_subject": sub.sync_subject,
                "is_exam_required": is_exam_required,
            }
        )
    return {
        "semester": semester,
        "year": year,
        "subjects": display_subjects,
        "subject_summaries": summaries,
        "missing_exam_subjects": missing_exam_subjects,
    }


@semester_router.api_route("/{semester}", response_class=RedirectResponse, methods=["GET", "HEAD"])
def semester_detail(
    request: Request,
    semester: str,
    year: str,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    """Legacy path: redirect to canonical /year/{year}/semester/{semester}."""
    return RedirectResponse(url=f"/year/{year}/semester/{semester}", status_code=303)


def _render_semesters_grid(request: Request, session: Session, year: str):
    """Render the semesters section partial (heading + filter + grid/no-data) respecting course and year."""
    sm = SemesterManager(session)
    cm = CourseManager(session)
    # Resolve active course from session (id preferred, fallback to code)
    sess = request.session
    cid = None
    active_course_id = sess.get("current_course_id")
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
        except Exception:
            cid = None
    if cid is None:
        code = sess.get("current_course_code")
        if code:
            course = cm.get_course_by_code(str(code))
            course_id = getattr(course, "id", None)
            if course_id is not None:
                cid = int(course_id)
                sess["current_course_id"] = cid

    if cid is not None:
        all_semesters = sm.get_semesters_for_course(cid)
    else:
        all_semesters = sm.get_all_semesters()

    try:
        y_int = int(str(year))
    except Exception:
        y_int = None

    semesters = [s for s in all_semesters if (y_int is None or int(s.year) == int(y_int))]
    # Include years and course_filter so the section header stays accurate
    from src.core.services.semester_manager import SemesterManager as _SM
    from src.core.services.course_manager import CourseManager as _CM
    sm2 = _SM(session)
    years = sm2.get_distinct_years_for_course(cid) if cid is not None else sm2.get_distinct_years()
    course_filter = None
    if cid is not None:
        course_filter = {
            "name": sess.get("current_course_name"),
            "code": sess.get("current_course_code"),
        }
    # Build subject_summaries for all semesters in this year, ordered by subject_code
    summaries = []
    subjects_table = cast(Table, getattr(Subject, "__table__"))
    semester_ids = [sem.id for sem in semesters]
    # Fetch all subjects for these semesters in one query, already sorted by subject_code
    all_subjects = session.exec(
        select(Subject)
        .where(col(Subject.semester_id).in_(semester_ids))
        .order_by(subjects_table.c.subject_code.asc())
    ).all() if semester_ids else []
    
    # Build semester lookup for getting semester names
    semester_lookup = {sem.id: sem.name for sem in semesters}
    
    # Iterate through subjects in their already-sorted order (by subject_code)
    for sub in all_subjects:
            sid = getattr(sub, "id", None)
            assignments = session.exec(select(Assignment).where(Assignment.subject_id == sid).order_by(Assignment.assessment)).all()
            exam = session.exec(select(Examination).where(Examination.subject_id == sid)).first()
            setting = session.exec(select(ExamSettings).where(ExamSettings.subject_id == sid)).first()
            ps_exam = bool(setting.ps_exam) if setting else False
            ps_factor = setting.ps_factor if setting else 40.0
            scaling = (ps_factor / 100.0) if ps_exam else 1.0
            exam_assignment = next((a for a in assignments if getattr(a, "is_exam", False)), None)
            assess_weight_sum = 0.0
            assess_weighted_total = 0.0
            assignment_weights = []
            for a in assignments:
                if getattr(a, "is_exam", False):
                    continue
                if a.grade_type == GradeType.NUMERIC.value:
                    if a.mark_weight not in (None, ""):
                        try:
                            w = float(a.mark_weight)
                            assess_weight_sum += w
                            assignment_weights.append(w)
                        except ValueError:
                            pass
                    if a.weighted_mark not in (None, ""):
                        try:
                            assess_weighted_total += float(a.weighted_mark)
                        except ValueError:
                            pass
            total_mark = sub.total_mark if sub.total_mark not in (None, 0) else None
            exam_weight = exam.exam_weight if exam else None
            final_exam_mark_weight = exam_weight
            effective_scoring_exam_weight = exam_weight * scaling if exam_weight is not None else None
            exam_mark = exam.exam_mark if exam else None
            is_exam_required = False
            # Get semester name from lookup
            sem_name = semester_lookup.get(sub.semester_id, "Unknown")
            summaries.append({
                "code": sub.subject_code,
                "name": sub.subject_name,
                "semester_name": sem_name,
                "assessment_mark": round(assess_weighted_total, 2),
                "assessment_weight": assess_weight_sum,
                "exam_mark": exam_mark,
                "exam_weight": exam_weight,
                "final_exam_mark_weight": final_exam_mark_weight,
                "effective_scoring_exam_weight": effective_scoring_exam_weight,
                "ps_exam": ps_exam,
                "ps_factor": ps_factor,
                "total_mark": total_mark,
                "sync_subject": sub.sync_subject,
                "is_exam_required": is_exam_required,
            })
    ctx = {"semesters": semesters, "selected_year": y_int, "years": years, "course_filter": course_filter, "subject_summaries": summaries}
    return _render(request, "partials/semesters_section.html", ctx)


def _render_semesters_section_string(request: Request, session: Session, year: str, oob: bool = False) -> str:
    """Return the rendered semesters section HTML string, optionally marked for out-of-band swap."""
    env = request.app.state.jinja_env
    sm = SemesterManager(session)
    cm = CourseManager(session)
    sess = request.session
    cid = None
    active_course_id = sess.get("current_course_id")
    if active_course_id is not None:
        try:
            cid = int(str(active_course_id).strip())
        except Exception:
            cid = None
    if cid is None:
        code = sess.get("current_course_code")
        if code:
            course = cm.get_course_by_code(str(code))
            course_id = getattr(course, "id", None)
            if course_id is not None:
                cid = int(course_id)
                sess["current_course_id"] = cid
    all_semesters = sm.get_semesters_for_course(cid) if cid is not None else sm.get_all_semesters()
    try:
        y_int = int(str(year))
    except Exception:
        y_int = None
    semesters = [s for s in all_semesters if (y_int is None or int(s.year) == int(y_int))]
    years = sm.get_distinct_years_for_course(cid) if cid is not None else sm.get_distinct_years()
    course_filter = None
    if cid is not None:
        course_filter = {"name": sess.get("current_course_name"), "code": sess.get("current_course_code")}
    html = env.get_template("partials/semesters_section.html").render(
        request=request,
        semesters=semesters,
        selected_year=y_int,
        years=years,
        course_filter=course_filter,
        oob=oob,
    )
    return html
