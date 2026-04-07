import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select, col
from typing import Sequence, List

from src.infrastructure.db.models import (
    Assignment,
    Examination,
    ExamSettings,
    Semester,
    Subject,
    SubjectPrerequisite,
    User,
    UserCourse,
)
from src.presentation.api.deps import get_session

router = APIRouter()

@router.get("/{user_id}", response_class=Response)
def export_user_data(user_id: int, session: Session = Depends(get_session)) -> Any:
    """
    Export all data associated with a specific user.
    """
    # 1. Fetch the User
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    # 2. Fetch UserCourse links to get relevant course_ids
    user_courses = session.exec(
        select(UserCourse).where(UserCourse.user_id == user_id)
    ).all()
    course_ids = [uc.course_id for uc in user_courses]

    if not course_ids:
        # User has no courses, return early with empty lists
        data = {
            "semesters": [],
            "subjects": [],
            "assignments": [],
            "examinations": [],
            "exam_settings": [],
            "subject_prerequisites": []
        }
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="marks_manager_export.json"'}
        )

    # 4. Fetch Semesters
    semesters = session.exec(select(Semester).where(col(Semester.course_id).in_(course_ids))).all()
    semester_ids = [s.id for s in semesters]

    # 5. Fetch Subjects
    subjects: Sequence[Subject] | List[Subject] = []
    subject_ids = []
    if semester_ids:
        subjects = session.exec(select(Subject).where(col(Subject.semester_id).in_(semester_ids))).all()
        subject_ids = [s.id for s in subjects]

    # 6. Fetch Assignments
    assignments: Sequence[Assignment] | List[Assignment] = []
    if subject_ids:
        assignments = session.exec(select(Assignment).where(col(Assignment.subject_id).in_(subject_ids))).all()

    # 7. Fetch Examinations
    examinations: Sequence[Examination] | List[Examination] = []
    if subject_ids:
        examinations = session.exec(select(Examination).where(col(Examination.subject_id).in_(subject_ids))).all()

    # 8. Fetch ExamSettings
    exam_settings: Sequence[ExamSettings] | List[ExamSettings] = []
    if subject_ids:
        exam_settings = session.exec(select(ExamSettings).where(col(ExamSettings.subject_id).in_(subject_ids))).all()

    # 9. Fetch SubjectPrerequisites
    subject_prerequisites: Sequence[SubjectPrerequisite] | List[SubjectPrerequisite] = []
    if subject_ids:
        subject_prerequisites = session.exec(
            select(SubjectPrerequisite).where(col(SubjectPrerequisite.subject_id).in_(subject_ids))
        ).all()

    # Assemble the final dictionary
    export_payload = {
        "semesters": jsonable_encoder(semesters),
        "subjects": jsonable_encoder(subjects),
        "assignments": jsonable_encoder(assignments),
        "examinations": jsonable_encoder(examinations),
        "exam_settings": jsonable_encoder(exam_settings),
        "subject_prerequisites": jsonable_encoder(subject_prerequisites)
    }

    return Response(
        content=json.dumps(export_payload, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="marks_manager_export.json"'}
    )
