import io
import pandas as pd
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select, col
from typing import Sequence, List

from src.infrastructure.db.models import (
    Assignment,
    Course,
    Examination,
    ExamSettings,
    GradeScale,
    Semester,
    Subject,
    SubjectPrerequisite,
    University,
    User,
    UserCourse,
)
from src.presentation.api.deps import get_session

router = APIRouter()

@router.get("/{user_id}", response_class=Response)
def export_user_data(user_id: int, session: Session = Depends(get_session)) -> Any:
    """
    Export all data associated with a specific user.
    Returns a downloadable Excel file containing the user's courses, semesters, 
    subjects, assignments, etc.
    """
    # 1. Fetch the User
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    # 2. Fetch UserCourse links (only the active/default course)
    user_courses = session.exec(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.is_default == True
        )
    ).all()
    course_ids = [uc.course_id for uc in user_courses]

    def construct_excel_response(data: dict, uid: int) -> Response:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for entity_name, records in data.items():
                if not isinstance(records, list):
                    records = [records] if records else []
                df = pd.DataFrame(jsonable_encoder(records))
                
                # Add human-readable subject_code to any sheet that references subject_id (except subjects)
                if 'subject_id' in df.columns and entity_name != 'subjects':
                    try:
                        subs = data.get("subjects", [])
                        subject_map = {s.id: (s.subject_code or s.subject_name) for s in subs}
                        
                        # Find the first occurrence of the string column name using basic python list index to keep type checkers happy
                        col_list = list(df.columns)
                        idx_val = col_list.index('subject_id')
                        
                        df.insert(idx_val + 1, 'subject_code', df['subject_id'].map(subject_map))
                    except Exception:
                        pass
                
                df.to_excel(writer, sheet_name=entity_name, index=False)
                
                # Enable AutoFilter dropdowns on the header row and freeze the top row for easy scrolling
                worksheet = writer.sheets[entity_name]
                worksheet.auto_filter.ref = worksheet.dimensions
                worksheet.freeze_panes = "A2"
                
            # Build the lookup dictionaries based on passed data for dropdown mappings
            courses_list = data.get("courses", [])
            semesters_list = data.get("semesters", [])
            subjects_list = data.get("subjects", [])
            
            # Format: '1 - COMP1000'
            lookups = {
                "courses": [f"{c.id} - {c.code or c.name}" for c in courses_list] if courses_list else [],
                "semesters": [f"{s.id} - {s.name}" for s in semesters_list] if semesters_list else [],
                "subjects": [f"{s.id} - {s.subject_code or s.subject_name}" for s in subjects_list] if subjects_list else []
            }
            
            max_len = max((len(v) for v in lookups.values()), default=0)
            if max_len > 0:
                padded_lookups: Dict[str, List[Any]] = {}
                for k, v in lookups.items():
                    padded: List[Any] = list(v)
                    padded.extend([""] * (max_len - len(v)))
                    padded_lookups[k] = padded
                
                df_lookups = pd.DataFrame(padded_lookups)
                df_lookups.to_excel(writer, sheet_name="_Lookups", index=False)
                
                ws_lookups = writer.book["_Lookups"]
                ws_lookups.sheet_state = "hidden"
                
                # Validation mapping: (Sheet Name, Target Column ID) -> Lookup Key
                validation_rules = [
                    ("user_courses", "course_id", "courses"),
                    ("semesters", "course_id", "courses"),
                    ("subjects", "semester_id", "semesters"),
                    ("assignments", "subject_id", "subjects"),
                    ("examinations", "subject_id", "subjects"),
                    ("exam_settings", "subject_id", "subjects"),
                    ("subject_prerequisites", "subject_id", "subjects"),
                    ("subject_prerequisites", "prerequisite_id", "subjects"),
                ]
                
                lookup_col_letters = {}
                for idx, col_name in enumerate(df_lookups.columns, start=1):
                    lookup_col_letters[col_name] = get_column_letter(idx)
                    
                for target_sheet, target_col, ref_lookup in validation_rules:
                    if target_sheet in writer.sheets and ref_lookup in lookup_col_letters:
                        ws_target = writer.sheets[target_sheet]
                        lookup_len = len(lookups[ref_lookup])
                        if lookup_len == 0:
                            continue
                            
                        # Find the target column letter natively
                        target_col_letter = None
                        for cell in ws_target[1]:
                            if cell.value == target_col:
                                target_col_letter = cell.column_letter
                                break
                                
                        if target_col_letter:
                            ref_col_letter = lookup_col_letters[ref_lookup]
                            dv = DataValidation(
                                type="list", 
                                formula1=f"'_Lookups'!${ref_col_letter}$2:${ref_col_letter}${lookup_len+1}",
                                allow_blank=True,
                                showErrorMessage=False # Allows manually pasting/leaving raw integer IDs as well
                            )
                            ws_target.add_data_validation(dv)
                            dv.add(f"{target_col_letter}2:{target_col_letter}1048576")
        
        output.seek(0)
        return Response(
            content=output.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="marks_manager_export.xlsx"'
            }
        )

    if not course_ids:
        # User has no courses, return early with empty lists
        data = {
            "user": user,
            "user_courses": [],
            "courses": [],
            "semesters": [],
            "subjects": [],
            "assignments": [],
            "examinations": [],
            "exam_settings": [],
            "subject_prerequisites": [],
            "universities": [],
            "grade_scales": []
        }
        return construct_excel_response(data, user_id)

    # 3. Fetch Courses
    courses = session.exec(select(Course).where(col(Course.id).in_(course_ids))).all()

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

    # 10. Fetch Global Reference Tables (Universities & Grade Scales linked to courses)
    universities: Sequence[University] | List[University] = []
    university_ids = [c.university_id for c in courses if c.university_id]
    if university_ids:
        universities = session.exec(select(University).where(col(University.id).in_(university_ids))).all()

    grade_scales: Sequence[GradeScale] | List[GradeScale] = []
    grade_scale_ids = [c.grading_scale_id for c in courses if c.grading_scale_id]
    if grade_scale_ids:
        grade_scales = session.exec(select(GradeScale).where(col(GradeScale.id).in_(grade_scale_ids))).all()

    # Assemble the final dictionary
    export_payload = {
        "user": user,
        "user_courses": user_courses,
        "courses": courses,
        "semesters": semesters,
        "subjects": subjects,
        "assignments": assignments,
        "examinations": examinations,
        "exam_settings": exam_settings,
        "subject_prerequisites": subject_prerequisites,
        "universities": universities,
        "grade_scales": grade_scales
    }

    return construct_excel_response(export_payload, user_id)
