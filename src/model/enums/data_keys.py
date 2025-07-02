from enum import Enum


class DataKeys(str, Enum):
    """
    DataKeys is an enumeration that defines string constants representing various keys
    used in the application for managing university marks. These keys are categorized
    into two groups: current keys and legacy keys.
    Current Keys:
    - SUBJECT_ASSESSMENT: Represents the key for subject assessment data.
    - UNWEIGHTED_MARK: Represents the key for unweighted marks.
    - WEIGHTED_MARK: Represents the key for weighted marks.
    - MARK_WEIGHT: Represents the key for the weight of a mark.
    - SUBJECT_NAME: Represents the key for the name of a subject.
    - TOTAL_MARK: Represents the key for the total mark of a subject.
    - SYNC_SUBJECT: Represents the key for syncing subject data.
    - ASSIGNMENTS: Represents the key for assignment data.
    - EXAMINATIONS: Represents the key for examination data.
    - EXAM_MARK: Represents the key for marks obtained in an exam.
    - EXAM_WEIGHT: Represents the key for the weight of an exam.
    - GRADE_TYPE: Represents the key for the type of grade.
    Legacy Keys (for backward compatibility):
    - SUBJECT_ASSESSMENT_LEGACY: Represents the legacy key for subject assessment data.
    - UNWEIGHTED_MARK_LEGACY: Represents the legacy key for unweighted marks.
    - WEIGHTED_MARK_LEGACY: Represents the legacy key for weighted marks.
    - MARK_WEIGHT_LEGACY: Represents the legacy key for the weight of a mark.
    - SUBJECT_NAME_LEGACY: Represents the legacy key for the name of a subject.
    - TOTAL_MARK_LEGACY: Represents the legacy key for the total mark of a subject.
    - SYNC_SUBJECT_LEGACY: Represents the legacy key for syncing subject data.
    - ASSIGNMENTS_LEGACY: Represents the legacy key for assignment data.
    - EXAMINATIONS_LEGACY: Represents the legacy key for examination data.
    - EXAM_MARK_LEGACY: Represents the legacy key for marks obtained in an exam.
    - EXAM_WEIGHT_LEGACY: Represents the legacy key for the weight of an exam.
    - GRADE_TYPE_LEGACY: Represents the legacy key for the type of grade.
    This enumeration is useful for ensuring consistency in key usage across the application
    and for maintaining backward compatibility with older versions of the data format.
    """

    # Current keys
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
