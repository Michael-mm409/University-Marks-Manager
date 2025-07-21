from enum import Enum


class SemesterName(str, Enum):
    AUTUMN = "Autumn"
    SPRING = "Spring"
    ANNUAL = "Annual"
    SUMMER = "Summer"


class GradeType(str, Enum):
    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"


class DataKeys(str, Enum):
    # Current keys
    SUBJECT_CODE = "subject_code"
    SUBJECT_ASSESSMENT = "subject_assessment"
    UNWEIGHTED_MARK = "unweighted_mark"
    WEIGHTED_MARK = "weighted_mark"
    MARK_WEIGHT = "mark_weight"
    SUBJECT_NAME = "subject_name"
    TOTAL_MARK = "total_mark"
    SYNC_SUBJECT = "sync_subject"
    ASSIGNMENTS = "assignments"
    EXAMINATIONS = "examinations"
    EXAM_MARK = "exam_mark"
    EXAM_WEIGHT = "exam_weight"
    GRADE_TYPE = "grade_type"

    # Legacy keys (for backward compatibility)
    SUBJECT_CODE_LEGACY = "Subject Code"
    SUBJECT_ASSESSMENT_LEGACY = "Subject Assessment"
    UNWEIGHTED_MARK_LEGACY = "Unweighted Mark"
    WEIGHTED_MARK_LEGACY = "Weighted Mark"
    MARK_WEIGHT_LEGACY = "Mark Weight"
    SUBJECT_NAME_LEGACY = "Subject Name"
    TOTAL_MARK_LEGACY = "Total Mark"
    SYNC_SUBJECT_LEGACY = "Sync Subject"
    ASSIGNMENTS_LEGACY = "Assignments"
    EXAMINATIONS_LEGACY = "Examinations"
    EXAM_MARK_LEGACY = "Exam Mark"
    EXAM_WEIGHT_LEGACY = "Exam Weight"
    GRADE_TYPE_LEGACY = "Grade Type"
