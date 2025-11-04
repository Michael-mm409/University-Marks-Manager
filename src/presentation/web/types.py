from typing import Sequence, List, Optional, Mapping, Union

from typing_extensions import TypedDict

from src.infrastructure.db.models import Semester, Subject, Assignment, Examination


class IndexContext(TypedDict):
    """
    Short description of the class.

    Attributes:
        attr1: Description.
    """
    semesters: Sequence[Semester]
    years: List[int]
    selected_year: Optional[int]
    current_year: str
    flash_message: Optional[str]
    course_filter: Optional[dict]


class SemesterSummary(TypedDict):
    """
    Short description of the class.

    Attributes:
        attr1: Description.
    """
    code: str
    name: str
    semester_name: str
    assessment_mark: float
    assessment_weight: float
    exam_mark: Optional[float]
    exam_weight: Optional[float]
    total_mark: Optional[float]
    sync_subject: bool


class SemesterContext(TypedDict):
    """
    Short description of the class.

    Attributes:
        attr1: Description.
    """
    semester: str
    year: str
    subjects: Sequence[Subject]
    subject_summaries: List[SemesterSummary]


class SubjectContext(TypedDict):
    """
    Short description of the class.

    Attributes:
        attr1: Description.
    """
    semester: str
    year: str
    subject: Subject
    assignments: Sequence[Assignment]
    examinations: Sequence[Examination]
    total_weighted: Optional[float]
    projected_total_weighted: Optional[float]
    total_weight_percent: Optional[float]
    average: Optional[float]
    final_total: Optional[str]
    total_mark: Optional[str]
    effective_exam_weight: Optional[float]
    required_exam_mark: Optional[float]
    requirement_status: Optional[str]
    ps_exam: bool
    ps_factor: Optional[float]
    raw_exam_percent: Optional[float]
    exam_mark: Optional[float]
    assignment_weighted_sum: Optional[float]
    assignment_weight_percent: Optional[float]
    exam_weighted_sum: Optional[float]
    effective_scoring_exam_weight: Optional[float]
    return_to: Optional[str]


TemplateContext = Union[IndexContext, SemesterContext, SubjectContext, Mapping[str, object]]
