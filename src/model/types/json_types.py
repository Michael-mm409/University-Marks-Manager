"""
Type definitions for JSON data structures in the University Marks Manager.

This module defines TypedDict classes that represent the structure of JSON data
used throughout the application. These types provide static type checking and
IDE support for JSON data manipulation while maintaining runtime compatibility
with regular dictionaries.

The data hierarchy follows this structure:
    RawDataDict (root)
    └── Dict[semester_name, SemesterDict]
        └── Dict[subject_code, SubjectDict]
            ├── List[AssignmentDict]
            └── ExaminationDict

Example:
    >>> from model.types.json_types import SubjectDict, AssignmentDict
    >>> assignment: AssignmentDict = {
    ...     "subject_assessment": "Quiz 1",
    ...     "weighted_mark": 4.0,
    ...     "mark_weight": 5.0,
    ...     "grade_type": "quiz"
    ... }
"""

from typing import Dict, List, Optional, Union

from typing_extensions import TypedDict


class AssignmentDict(TypedDict, total=False):
    """Structure of assignment data in JSON.

    Represents individual assignment/assessment data within a subject.
    Uses total=False to allow partial dictionaries during data loading.

    Attributes:
        subject_assessment: Name/title of the assignment or assessment
        weighted_mark: Actual points scored (can be float or string from JSON)
        unweighted_mark: Decimal percentage representation (0.0-1.0)
        mark_weight: Maximum possible points for this assignment (also weight %)
        grade_type: Category of assessment ("assignment", "quiz", "project", etc.)

    Example:
        >>> assignment: AssignmentDict = {
        ...     "subject_assessment": "Assignment 1",
        ...     "weighted_mark": 14.5,
        ...     "unweighted_mark": 0.967,
        ...     "mark_weight": 15.0,
        ...     "grade_type": "assignment"
        ... }
    """

    subject_assessment: str
    weighted_mark: Union[float, str]  # String during JSON loading, float after parsing
    unweighted_mark: Optional[float]
    mark_weight: Optional[float]
    grade_type: str


class ExaminationDict(TypedDict, total=False):
    """Structure of examination data in JSON.

    Represents exam/final assessment data for a subject. Currently supports
    a single exam per subject but could be extended for multiple exams.

    Attributes:
        exam_mark: Points scored on the exam
        exam_weight: Maximum possible points for the exam

    Example:
        >>> exam: ExaminationDict = {
        ...     "exam_mark": 42.5,
        ...     "exam_weight": 50.0
        ... }
    """

    exam_mark: float
    exam_weight: float


class SubjectDict(TypedDict, total=False):
    """Structure of subject data in JSON.

    Represents complete data for a single subject/course, including all
    assignments, examinations, and metadata. Forms the core data structure
    for academic performance tracking.

    Attributes:
        subject_code: Official course code (e.g., "CSCI251", "MATH142")
        subject_name: Full descriptive name of the subject
        assignments: List of all assignments/assessments for this subject
        examinations: Exam data (if applicable)
        sync_subject: Whether this subject syncs with external systems
        total_mark: Final calculated grade/mark for the subject

    Example:
        >>> subject: SubjectDict = {
        ...     "subject_code": "CSCI251",
        ...     "subject_name": "Advanced Programming",
        ...     "assignments": [assignment1, assignment2],
        ...     "examinations": {"exam_mark": 45.0, "exam_weight": 50.0},
        ...     "sync_subject": True,
        ...     "total_mark": 78.5
        ... }
    """

    subject_code: str
    subject_name: str
    assignments: List[AssignmentDict]
    examinations: ExaminationDict
    sync_subject: bool
    total_mark: float


class SemesterDict(TypedDict):
    """Structure of semester data in JSON.

    Maps subject codes to their complete subject data for a specific semester.
    This is an intermediate structure between the root data and individual subjects.

    Note: Uses __root__ pattern for type safety with dynamic keys, but in practice
    this is just Dict[str, SubjectDict] where keys are subject codes.

    Structure:
        {
            "CSCI251": SubjectDict,
            "MATH142": SubjectDict,
            "PHYS141": SubjectDict,
            ...
        }

    Example:
        >>> semester: Dict[str, SubjectDict] = {
        ...     "CSCI251": {
        ...         "subject_code": "CSCI251",
        ...         "subject_name": "Advanced Programming",
        ...         "assignments": [...],
        ...         # ... other subject data
        ...     }
        ... }
    """

    __root__: Dict[str, SubjectDict]


class RawDataDict(TypedDict):
    """Root JSON structure for the entire University Marks Manager dataset.

    Represents the complete data structure loaded from JSON files, organized
    by semester and then by subject. This is the top-level container for all
    academic data in the application.

    Structure:
        {
            "2024 Session 1": {
                "CSCI251": SubjectDict,
                "MATH142": SubjectDict,
                ...
            },
            "2024 Session 2": {
                "PHYS141": SubjectDict,
                "ENGG100": SubjectDict,
                ...
            }
        }

    Note: Uses __root__ pattern to indicate this is a mapping type with
    dynamic keys (semester names).

    Example:
        >>> data: Dict[str, Dict[str, SubjectDict]] = {
        ...     "2024 Session 1": {
        ...         "CSCI251": subject_data,
        ...         "MATH142": math_data
        ...     },
        ...     "2024 Session 2": {
        ...         "PHYS141": physics_data
        ...     }
        ... }
    """

    __root__: Dict[str, Dict[str, SubjectDict]]
