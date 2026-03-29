from typing import Any, Dict, List, Optional
import io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session
from pydantic import BaseModel

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

@router.post("/{user_id}", response_model=Dict[str, Any])
async def import_user_data(
    user_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Import user data from Excel export.
    
    Enforces strict import order to prevent FK constraint errors:
    1. GradeScales, Universities
    2. Courses
    3. UserCourses (with forced user_id from endpoint)
    4. Semesters
    5. Subjects
    6. Assignments, Examinations, ExamSettings, SubjectPrerequisites
    """
    try:
        # Verify target user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found.",
            )

        content = await file.read()
        try:
            excel_data = pd.read_excel(io.BytesIO(content), sheet_name=None)
            
            # Helper to safely convert DataFrame to list of dicts with NaNs as None
            def get_sheet_records(sheet_name: str) -> List[Dict[str, Any]]:
                if sheet_name not in excel_data:
                    return []
                df = excel_data[sheet_name]
                records = df.to_dict(orient="records")
                
                result: List[Dict[str, Any]] = []
                for record in records:
                    clean_record: Dict[str, Any] = {}
                    for k, v in record.items():
                        key_str = str(k)
                        
                        # Ignore the injected subject_code helper column (except on the subjects sheet where it is real)
                        if key_str == "subject_code" and sheet_name != "subjects":
                            continue
                        
                        # Translate Excel dropdown values (e.g. "12 - COMP1000") back to integer IDs safely
                        if key_str.endswith("_id") and isinstance(v, str) and " - " in v:
                            try:
                                v = int(v.split(" - ")[0])
                            except ValueError:
                                pass
                                
                        if pd.isna(v):
                            clean_record[key_str] = None
                        else:
                            clean_record[key_str] = v
                    result.append(clean_record)
                return result

            payload = {
                "grade_scales": get_sheet_records("grade_scales"),
                "universities": get_sheet_records("universities"),
                "courses": get_sheet_records("courses"),
                "user_courses": get_sheet_records("user_courses"),
                "semesters": get_sheet_records("semesters"),
                "subjects": get_sheet_records("subjects"),
                "assignments": get_sheet_records("assignments"),
                "examinations": get_sheet_records("examinations"),
                "exam_settings": get_sheet_records("exam_settings"),
                "subject_prerequisites": get_sheet_records("subject_prerequisites")
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Excel file or format: {str(e)}")

        imported_counts = {
            "grade_scales": 0,
            "universities": 0,
            "courses": 0,
            "user_courses": 0,
            "semesters": 0,
            "subjects": 0,
            "assignments": 0,
            "examinations": 0,
            "exam_settings": 0,
            "subject_prerequisites": 0,
        }

        # STEP 1: Import GradeScales and Universities
        for gs_data in payload.get("grade_scales", []):
            gs = GradeScale(**gs_data)
            session.merge(gs)
            imported_counts["grade_scales"] += 1

        for uni_data in payload.get("universities", []):
            uni = University(**uni_data)
            session.merge(uni)
            imported_counts["universities"] += 1

        session.flush()

        # STEP 2: Import Courses
        for course_data in payload.get("courses", []):
            course = Course(**course_data)
            session.merge(course)
            imported_counts["courses"] += 1

        session.flush()

        # STEP 3: Import UserCourses (force user_id mapping)
        for uc_data in payload.get("user_courses", []):
            uc_data["user_id"] = user_id
            uc = UserCourse(**uc_data)
            session.merge(uc)
            imported_counts["user_courses"] += 1

        session.flush()

        # STEP 4: Import Semesters
        for sem_data in payload.get("semesters", []):
            sem = Semester(**sem_data)
            session.merge(sem)
            imported_counts["semesters"] += 1

        session.flush()

        # STEP 5: Import Subjects
        for subj_data in payload.get("subjects", []):
            subj = Subject(**subj_data)
            session.merge(subj)
            imported_counts["subjects"] += 1

        session.flush()

        # STEP 6: Import Leaves
        for assign_data in payload.get("assignments", []):
            assign = Assignment(**assign_data)
            
            # Automatically calculate unweighted_mark if it's left blank in Excel
            if assign.unweighted_mark is None and assign.weighted_mark is not None and assign.mark_weight:
                try:
                    weight = float(assign.mark_weight)
                    if weight > 0:
                        assign.unweighted_mark = round(float(assign.weighted_mark) / weight, 4)
                except (ValueError, TypeError):
                    pass
                    
            session.merge(assign)
            imported_counts["assignments"] += 1

        for exam_data in payload.get("examinations", []):
            exam = Examination(**exam_data)
            session.merge(exam)
            imported_counts["examinations"] += 1

        for exam_set_data in payload.get("exam_settings", []):
            exam_set = ExamSettings(**exam_set_data)
            session.merge(exam_set)
            imported_counts["exam_settings"] += 1

        for prereq_data in payload.get("subject_prerequisites", []):
            prereq = SubjectPrerequisite(**prereq_data)
            session.merge(prereq)
            imported_counts["subject_prerequisites"] += 1

        session.flush()
        session.commit()

        return {
            "success": True,
            "message": f"Successfully imported data for user {user_id}",
            "imported": imported_counts,
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Import failed: {str(e)}",
        )
