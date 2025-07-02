"""
Type definitions for JSON data structures in the University Marks Manager.
"""

from typing import Dict, List, Optional, Union

from typing_extensions import TypedDict


class AssignmentDict(TypedDict, total=False):
    """Structure of assignment data in JSON."""

    subject_assessment: str
    weighted_mark: Union[float, str]
    unweighted_mark: Optional[float]
    mark_weight: Optional[float]
    grade_type: str


class ExaminationDict(TypedDict, total=False):
    """Structure of examination data in JSON."""

    exam_mark: float
    exam_weight: float


class SubjectDict(TypedDict, total=False):
    """Structure of subject data in JSON."""

    subject_code: str
    subject_name: str
    assignments: List[AssignmentDict]
    examinations: ExaminationDict
    sync_subject: bool
    total_mark: float


class SemesterDict(TypedDict):
    """Structure of semester data in JSON (subject_code -> SubjectDict)."""

    __root__: Dict[str, SubjectDict]


class RawDataDict(TypedDict):
    """Root JSON structure (semester_name -> SemesterDict)."""

    __root__: Dict[str, Dict[str, SubjectDict]]
