"""Authentication routes for user login/signup/logout."""
from typing import Any, Optional, List, cast
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select, col, func
from sqlalchemy.orm import selectinload
from src.infrastructure.db.models import User, UserCourse, Course, GradeScale, University
import bcrypt
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import os

from src.presentation.api.deps import get_session
from src.core.services.course_manager import CourseManager
from src.presentation.web.template_helpers import _render

router = APIRouter()

# Argon2 hasher for new passwords and upgrades
ph = PasswordHasher()

# SECRET_PEPPER: append to passwords before hashing/verifying for added secret
# Keep empty if not set to preserve backwards compatibility for bcrypt verification
SECRET_PEPPER = os.getenv("SECRET_PEPPER", "")


def hash_password(password: str) -> str:
    """Hash a password using Argon2id and the configured SECRET_PEPPER."""
    return ph.hash(password + SECRET_PEPPER)


def verify_and_upgrade_password(
    password: str,
    password_hash: str,
    session: Optional[Session] = None,
    user: Optional[User] = None,
) -> bool:
    """Verify a password against either Argon2 or bcrypt hashes.

    If the stored hash is a bcrypt hash and verification succeeds, re-hash
    the password with Argon2id and update the user's record in the database
    when `session` and `user` are provided.
    """
    try:
        # Argon2 hashes start with $argon2id$
        if password_hash.startswith("$argon2id$"):
            try:
                ph.verify(password_hash, password + SECRET_PEPPER)
                # If argon2 parameters changed, rehash and store
                if session is not None and user is not None and ph.check_needs_rehash(password_hash):
                    try:
                        new_hash = ph.hash(password + SECRET_PEPPER)
                        user.password_hash = new_hash
                        session.add(user)
                        session.commit()
                        session.refresh(user)
                    except Exception:
                        pass
                return True
            except argon2_exceptions.VerifyMismatchError:
                return False
            except Exception:
                return False

        # Bcrypt common prefixes: $2a$, $2b$, $2y$
        if password_hash.startswith("$2a$") or password_hash.startswith("$2b$") or password_hash.startswith("$2y$"):
            try:
                ok = bcrypt.checkpw(password.encode(), password_hash.encode())
                if ok and session is not None and user is not None:
                    try:
                        # Re-hash with Argon2 and persist
                        new_hash = ph.hash(password + SECRET_PEPPER)
                        user.password_hash = new_hash
                        session.add(user)
                        session.commit()
                        session.refresh(user)
                    except Exception:
                        pass
                return ok
            except Exception:
                return False

        # Fallback: try bcrypt check
        try:
            # Last-resort: try bcrypt without pepper for legacy compatibility
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except Exception:
            return False
    except Exception:
        return False


@router.api_route("/login", methods=["GET", "HEAD"], response_class=HTMLResponse)
def login_page(request: Request):
    """Render the login page."""
    # If already logged in, redirect to home
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)
    
    error = request.query_params.get("error")
    return _render(request, "login.html", {"error": error})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """Handle user login."""
    username = username.strip()
    
    # Find user by username
    user = session.exec(select(User).where(User.username == username)).first()

    if not user:
        return RedirectResponse(url="/login?error=Invalid username or password", status_code=303)

    # Verify password (supports Argon2 and legacy bcrypt). If a legacy
    # bcrypt hash is used and verification succeeds, the helper will
    # re-hash the password with Argon2 and update the user's record.
    if not verify_and_upgrade_password(password, user.password_hash, session=session, user=user):
        return RedirectResponse(url="/login?error=Invalid username or password", status_code=303)
    
    # Set session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    
    # Set default course if available
    user_course = session.exec(
        select(UserCourse).where(
            UserCourse.user_id == user.id,
            UserCourse.is_default == True
        )
    ).first()
    
    if user_course:
        request.session["current_course_id"] = user_course.course_id
        course = session.get(Course, user_course.course_id)
        if course:
            request.session["current_course_name"] = course.name
            request.session["current_course_code"] = course.code
    
    return RedirectResponse(url="/?selected=1", status_code=303)


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    """Render the signup page."""
    # If already logged in, redirect to home
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)
    
    error = request.query_params.get("error")
    return _render(request, "signup.html", {"error": error})


@router.post("/signup")
def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    session: Session = Depends(get_session),
):
    """Handle user registration."""
    username = username.strip()
    email = email.strip()
    
    # Validation
    if not username or len(username) < 3:
        return RedirectResponse(url="/signup?error=Username must be at least 3 characters", status_code=303)
    
    if not email or "@" not in email:
        return RedirectResponse(url="/signup?error=Invalid email address", status_code=303)
    
    if not password or len(password) < 8:
        return RedirectResponse(url="/signup?error=Password must be at least 8 characters", status_code=303)
    
    if password != password_confirm:
        return RedirectResponse(url="/signup?error=Passwords do not match", status_code=303)
    
    # Check if username already exists
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        return RedirectResponse(url="/signup?error=Username already taken", status_code=303)
    
    # Check if email already exists
    existing_email = session.exec(select(User).where(User.email == email)).first()
    if existing_email:
        return RedirectResponse(url="/signup?error=Email already registered", status_code=303)
    
    # Create new user
    hashed_password = hash_password(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Automatically log in the new user
    request.session["user_id"] = new_user.id
    request.session["username"] = new_user.username
    
    return RedirectResponse(url="/?selected=1", status_code=303)


@router.get("/logout")
def logout(request: Request):
    """Handle user logout."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, session: Session = Depends(get_session)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    # SQLAlchemy 2.x requires class-bound attributes (not string relationship names).
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(cast(Any, User.user_courses)).selectinload(cast(Any, UserCourse.course))
        )
    )
    user = session.exec(statement).first()
    
    if not user:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)
    
    # Compute courses NOT associated with this user
    assigned_course_ids = session.exec(
        select(UserCourse.course_id).where(UserCourse.user_id == user_id)
    ).all()

    if assigned_course_ids:
        available_courses = session.exec(
            select(Course).where(col(Course.id).not_in(assigned_course_ids))
        ).all()
    else:
        available_courses = session.exec(select(Course)).all()

    # Grading scales logic
    all_scales = session.exec(select(GradeScale)).all()
    seen_scale_names = set()
    grading_scales = []
    for scale in all_scales:
        if scale.scale_name not in seen_scale_names:
            seen_scale_names.add(scale.scale_name)
            grading_scales.append(scale)

    universities = session.exec(select(University)).all()

    # Build a list of (max_gpa_int, scale_name) pairs for every scale that has
    # at least one band_type="both" row — used by the profile GPA scale selector
    # and the Add Grade Band form.  Sorted ascending so 4-pt comes before 7-pt.
    gpa_scale_rows = session.exec(
        select(GradeScale.scale_name, func.max(GradeScale.gpa_point))
        .where(GradeScale.band_type == "both")
        .group_by(GradeScale.scale_name)
        .order_by(func.max(GradeScale.gpa_point))
    ).all()
    gpa_scale_options = [
        (int(row[1]), row[0])
        for row in gpa_scale_rows
        if row[1] is not None
    ]

    # Richer per-scale data for the "Registered Scales" profile card.
    # Fetches every band (grade letter + gpa_point) for each scale and groups
    # them so the template can render one card per scale with its bands listed.
    _band_rows = session.exec(
        select(GradeScale.scale_name, GradeScale.grade, GradeScale.gpa_point)
        .where(GradeScale.band_type == "both")
        .order_by(GradeScale.scale_name, GradeScale.gpa_point.desc())
    ).all()
    _scale_map: dict[str, dict] = {}
    for _sname, _grade, _gpa in _band_rows:
        if _sname not in _scale_map:
            _scale_map[_sname] = {"scale_name": _sname, "max_gpa": int(_gpa), "bands": []}
        _scale_map[_sname]["bands"].append(_grade)
    gpa_scale_cards = sorted(_scale_map.values(), key=lambda x: x["max_gpa"])

    return _render(request, "profile.html", {
        "user": user,
        "courses": user.user_courses,
        "available_courses": available_courses,
        "grading_scales": grading_scales,
        "universities": universities,
        "gpa_scale_options": gpa_scale_options,
        "gpa_scale_cards": gpa_scale_cards,
    })


@router.post("/profile/change-password")
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    session: Session = Depends(get_session),
):
    """Change the current user's password after verifying the current one.

    Uses the existing Argon2id + PEPPER logic for verification and storage.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = session.get(User, user_id)
    if not user:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)

    # Verify current password (this will also migrate bcrypt hashes if present)
    if not verify_and_upgrade_password(current_password, user.password_hash, session=session, user=user):
        return RedirectResponse(url="/profile?error=Current password is incorrect", status_code=303)

    # Validate new password
    if not new_password or len(new_password) < 8:
        return RedirectResponse(url="/profile?error=New password must be at least 8 characters", status_code=303)

    if new_password != confirm_password:
        return RedirectResponse(url="/profile?error=New passwords do not match", status_code=303)

    try:
        # Hash new password with Argon2id + PEPPER
        user.password_hash = hash_password(new_password)
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception:
        return RedirectResponse(url="/profile?error=Failed to update password", status_code=303)

    return RedirectResponse(url="/profile", status_code=303)



@router.get("/courses/create", response_class=HTMLResponse)
def course_create_page(request: Request, session: Session = Depends(get_session)):
    """Render a full-page form for creating a new course/program."""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Available universities
    universities = session.exec(select(University)).all()

    # Provide a list of unique grading scale names (one row per scale)
    all_scales = session.exec(select(GradeScale)).all()
    seen_scale_names = set()
    grading_scales = []
    for scale in all_scales:
        if scale.scale_name not in seen_scale_names:
            seen_scale_names.add(scale.scale_name)
            grading_scales.append(scale)

    return _render(request, "course_create.html", {
        "universities": universities,
        "grading_scales": grading_scales,
    })


@router.post("/courses/create")
def course_create_submit(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    grading_scale_id: str = Form(...),
    university_id: str = Form(None),
    new_university_name: str = Form(None),
    custom_grading_scale: Optional[str] = Form(None),
    custom_grades: Optional[List[str]] = Form(None),
    custom_labels: Optional[List[str]] = Form(None),
    custom_min_marks: Optional[List[float]] = Form(None),
    custom_gpa_points: Optional[List[float]] = Form(None),
    custom_band_types: Optional[List[str]] = Form(None),
    session: Session = Depends(get_session),
):
    """Handle course creation form submission including custom grading bands."""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Handle grading scale: either existing id or create custom when "other" is selected
    gs_id: Optional[int] = None
    if grading_scale_id and grading_scale_id != "other":
        try:
            gs_id = int(str(grading_scale_id))
        except Exception:
            return RedirectResponse(url="/courses/create?error=Invalid grading scale selected", status_code=303)
    elif grading_scale_id == "other":
        # Validate custom scale data
        if not custom_grading_scale or not custom_grades or not custom_labels or not custom_min_marks or not custom_gpa_points:
            return RedirectResponse(url="/courses/create?error=Missing custom grading scale data", status_code=303)

        scale_name = custom_grading_scale.strip()
        if not scale_name:
            return RedirectResponse(url="/courses/create?error=Custom scale name is required", status_code=303)

        scale_ids: List[int] = []
        for i in range(len(custom_grades)):
            grade = (custom_grades[i] or "").strip()
            label = (custom_labels[i] or "").strip()
            if not grade or not label:
                continue
            try:
                min_mark = float(custom_min_marks[i]) if custom_min_marks[i] is not None else 0.0
            except Exception:
                min_mark = 0.0
            try:
                gpa_point = float(custom_gpa_points[i]) if custom_gpa_points[i] is not None else 0.0
            except Exception:
                gpa_point = 0.0
            band_type = (
                custom_band_types[i]
                if custom_band_types is not None and i < len(custom_band_types)
                else "both"
            )

            existing = session.exec(
                select(GradeScale).where(
                    GradeScale.scale_name == scale_name,
                    GradeScale.grade == grade,
                    GradeScale.band_type == band_type,
                )
            ).first()
            if existing:
                scale_ids.append(existing.id)  # type: ignore[arg-type]
            else:
                gs = GradeScale(
                    scale_name=scale_name,
                    grade=grade,
                    label=label,
                    min_mark=min_mark,
                    gpa_point=gpa_point,
                    band_type=band_type,
                )
                session.add(gs)
                session.commit()
                session.refresh(gs)
                scale_ids.append(gs.id)  # type: ignore[arg-type]

        if not scale_ids:
            return RedirectResponse(url="/courses/create?error=At least one grading band is required", status_code=303)

        gs_id = scale_ids[0]

    # Parse optional university id
    uni_id = None
    if university_id and university_id != "add_new":
        try:
            uni_id = int(university_id)
        except Exception:
            uni_id = None

    if gs_id is None:
        return RedirectResponse(url="/courses/create?error=Invalid grading scale selected", status_code=303)

    cm = CourseManager(session)
    course = cm.create_course(
        name=name,
        code=code,
        grading_scale_id=gs_id,
        university_id=uni_id,
        new_university_name=new_university_name if university_id == "add_new" else None,
    )

    # Attach the new course to the user (make default if first)
    user_courses = session.exec(
        select(UserCourse).where(UserCourse.user_id == user_id)
    ).all()
    is_default = len(user_courses) == 0

    user_course = UserCourse(
        user_id=user_id,
        course_id=course.id,  # type: ignore[arg-type]
        is_default=is_default,
    )
    session.add(user_course)
    session.commit()

    if is_default:
        request.session["current_course_id"] = course.id
        request.session["current_course_name"] = course.name
        request.session["current_course_code"] = course.code

    return RedirectResponse(url=f"/courses/{course.id}", status_code=303)

@router.post("/profile/add-course")
def add_course_to_user(
    request: Request,
    course_id: int = Form(...),
    session: Session = Depends(get_session)
):
    """Add a course to the current user."""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    # Check if already assigned
    existing = session.exec(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id
        )
    ).first()
    
    if existing:
        return RedirectResponse(url="/profile?error=Course already assigned", status_code=303)
    
    # Check if user has any courses - if not, make this the default
    user_courses = session.exec(
        select(UserCourse).where(UserCourse.user_id == user_id)
    ).all()
    
    is_default = len(user_courses) == 0
    
    # Create association
    user_course = UserCourse(
        user_id=user_id,
        course_id=course_id,
        is_default=is_default
    )
    session.add(user_course)
    session.commit()
    
    # If this is the default, update session
    if is_default:
        course = session.get(Course, course_id)
        if course:
            request.session["current_course_id"] = course.id
            request.session["current_course_name"] = course.name
            request.session["current_course_code"] = course.code
    
    return RedirectResponse(url="/profile", status_code=303)


@router.post("/profile/create-course")
def create_course_for_user(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    grading_scale_id: str = Form(...),
    university_id: str = Form(None),
    new_university_name: str = Form(None),
    custom_grading_scale: Optional[str] = Form(None),
    custom_grades: Optional[List[str]] = Form(None),
    custom_labels: Optional[List[str]] = Form(None),
    custom_min_marks: Optional[List[float]] = Form(None),
    custom_gpa_points: Optional[List[float]] = Form(None),
    custom_band_types: Optional[List[str]] = Form(None),
    session: Session = Depends(get_session),
):
    """Create a brand new course and attach it to the current user.

    This is used by the inline "Create New Course" form on the profile page.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Handle grading scale: either existing id or create custom when "other" is selected
    gs_id: Optional[int] = None
    if grading_scale_id and grading_scale_id != "other":
        try:
            gs_id = int(str(grading_scale_id))
        except Exception:
            return RedirectResponse(url="/profile?error=Invalid grading scale selected", status_code=303)
    elif grading_scale_id == "other":
        # Validate custom scale data
        if not custom_grading_scale or not custom_grades or not custom_labels or not custom_min_marks or not custom_gpa_points:
            return RedirectResponse(url="/profile?error=Missing custom grading scale data", status_code=303)

        scale_name = custom_grading_scale.strip()
        if not scale_name:
            return RedirectResponse(url="/profile?error=Custom scale name is required", status_code=303)

        scale_ids: List[int] = []
        for i in range(len(custom_grades)):
            grade = (custom_grades[i] or "").strip()
            label = (custom_labels[i] or "").strip()
            if not grade or not label:
                continue
            try:
                min_mark = float(custom_min_marks[i]) if custom_min_marks[i] is not None else 0.0
            except Exception:
                min_mark = 0.0
            try:
                gpa_point = float(custom_gpa_points[i]) if custom_gpa_points[i] is not None else 0.0
            except Exception:
                gpa_point = 0.0
            band_type = (
                custom_band_types[i]
                if custom_band_types is not None and i < len(custom_band_types)
                else "both"
            )

            existing = session.exec(
                select(GradeScale).where(
                    GradeScale.scale_name == scale_name,
                    GradeScale.grade == grade,
                    GradeScale.band_type == band_type,
                )
            ).first()
            if existing:
                scale_ids.append(existing.id)  # type: ignore[arg-type]
            else:
                gs = GradeScale(
                    scale_name=scale_name,
                    grade=grade,
                    label=label,
                    min_mark=min_mark,
                    gpa_point=gpa_point,
                    band_type=band_type,
                )
                session.add(gs)
                session.commit()
                session.refresh(gs)
                scale_ids.append(gs.id)  # type: ignore[arg-type]

        if not scale_ids:
            return RedirectResponse(url="/profile?error=Failed to create custom grading scale", status_code=303)

        gs_id = scale_ids[0]

    # Parse optional university id
    uni_id = None
    if university_id and university_id != "add_new":
        try:
            uni_id = int(university_id)
        except Exception:
            uni_id = None

    if gs_id is None:
        return RedirectResponse(url="/profile?error=Invalid grading scale selected", status_code=303)

    cm = CourseManager(session)
    course = cm.create_course(
        name=name,
        code=code,
        grading_scale_id=gs_id,
        university_id=uni_id,
        new_university_name=new_university_name if university_id == "add_new" else None,
    )

    # Attach the new course to the user (make default if first)
    user_courses = session.exec(
        select(UserCourse).where(UserCourse.user_id == user_id)
    ).all()
    is_default = len(user_courses) == 0

    user_course = UserCourse(
        user_id=user_id,
        course_id=course.id,  # type: ignore[arg-type]
        is_default=is_default,
    )
    session.add(user_course)
    session.commit()

    if is_default:
        request.session["current_course_id"] = course.id
        request.session["current_course_name"] = course.name
        request.session["current_course_code"] = course.code

    return RedirectResponse(url="/profile", status_code=303)


@router.post("/profile/remove-course/{user_course_id}")
def remove_course_from_user(
    request: Request,
    user_course_id: int,
    session: Session = Depends(get_session)
):
    """Remove a course from the current user."""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    # Get the user course
    user_course = session.get(UserCourse, user_course_id)
    if not user_course or user_course.user_id != user_id:
        return RedirectResponse(url="/profile?error=Course not found", status_code=303)
    
    was_default = user_course.is_default
    course_id = user_course.course_id
    
    session.delete(user_course)
    session.commit()
    
    # If we removed the default, set a new default
    if was_default:
        remaining = session.exec(
            select(UserCourse).where(UserCourse.user_id == user_id)
        ).first()
        
        if remaining:
            remaining.is_default = True
            session.add(remaining)
            session.commit()
            
            course = session.get(Course, remaining.course_id)
            if course:
                request.session["current_course_id"] = course.id
                request.session["current_course_name"] = course.name
                request.session["current_course_code"] = course.code
        else:
            # No courses left, clear session
            request.session.pop("current_course_id", None)
            request.session.pop("current_course_name", None)
            request.session.pop("current_course_code", None)
    
    return RedirectResponse(url="/profile", status_code=303)


@router.post("/profile/set-default/{user_course_id}")
def set_default_course(
    request: Request,
    user_course_id: int,
    session: Session = Depends(get_session)
):
    """Set a course as the default for the current user."""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    # Get the user course
    user_course = session.get(UserCourse, user_course_id)
    if not user_course or user_course.user_id != user_id:
        return RedirectResponse(url="/profile?error=Course not found", status_code=303)
    
    # Unset all defaults for this user
    user_courses = session.exec(
        select(UserCourse).where(UserCourse.user_id == user_id)
    ).all()
    
    for uc in user_courses:
        uc.is_default = (uc.id == user_course_id)
        session.add(uc)
    
    session.commit()
    
    # Update session
    course = session.get(Course, user_course.course_id)
    if course:
        request.session["current_course_id"] = course.id
        request.session["current_course_name"] = course.name
        request.session["current_course_code"] = course.code
    
    return RedirectResponse(url="/profile", status_code=303)
