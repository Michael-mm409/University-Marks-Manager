from typing import Sequence, List, Optional, Mapping, Union, TYPE_CHECKING
from typing_extensions import TypedDict

# Use TYPE_CHECKING to prevent circular imports at runtime
if TYPE_CHECKING:
    from src.infrastructure.db.models import Semester, Subject, Assignment, Examination, SubjectPrerequisite
else:
    # Fallback to avoid runtime NameErrors if needed, or keep as strings below
    Semester = "Semester"
    Subject = "Subject"
    Assignment = "Assignment"
    Examination = "Examination"
    SubjectPrerequisite = "SubjectPrerequisite"

class IndexContext(TypedDict):
    semesters: Sequence["Semester"]
    years: List[int]
    selected_year: Optional[int]
    current_year: str
    flash_message: Optional[str]
    course_filter: Optional[dict]
    wam: Optional[float]
    gpa: Optional[float]
    grade_counts: Optional[dict[str, int]]
    no_courses_warning: Optional[bool]
    user_courses: List[dict]
    username: Optional[str]
    subjects_by_semester: dict[int, list]
    # completed_codes: List[str]


class SemesterSummary(TypedDict):
    """
    Short description of the class.

    Attributes:
        attr1: Description.
    """
    code: str
    name: str
    semester_name: str
    credit_points: Optional[int]
    assessment_unweighted: float
    assessment_unweighted_contribution: float
    assessment_mark: Optional[float]
    assessment_weight: float
    exam_mark: Optional[float]
    exam_weight: Optional[float]
    final_exam_mark_weight: Optional[float]
    effective_scoring_exam_weight: Optional[float]
    ps_exam: bool
    ps_factor: Optional[float]
    total_mark: Optional[float]
    is_exam_required: bool
    has_exam: bool
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
    missing_exam_subjects: List[str]


class SubjectContext(TypedDict):
    semester: str
    year: str
    subject: "Subject"
    assignments: Sequence["Assignment"]
    examinations: Sequence["Examination"]
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
    legacy_exam_mark: Optional[float]
    legacy_exam_weight: Optional[float]
    has_legacy_exam: bool
    has_assignment_exam: bool
    count_s: int
    count_u: int
    count_hd: int
    count_d: int
    count_c: int
    count_p: int
    count_ps: int
    count_f: int
    final_exam_mark_weight: Optional[float]
    summary_exam_mark: Optional[float]
    error_messages: List[str]
    prerequisites: Sequence["SubjectPrerequisite"]
    required_for: Sequence["SubjectPrerequisite"]
    assignment_unweighted_sum: Optional[float]
    overall_assignment_unweighted: Optional[float]

TemplateContext = Union[IndexContext, SemesterContext, SubjectContext, Mapping[str, object]]
