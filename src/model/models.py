from dataclasses import dataclass, field
from typing import List, Literal, Optional, Union


@dataclass
class Assignment:
    """
    Represents an assignment with its associated marks and weight.
    Attributes:
        subject_assessment (str): The name or identifier of the subject assessment.
        unweighted_mark (float): The raw mark obtained for the assignment.
        weighted_mark (float): The mark adjusted by the weight of the assignment.
        mark_weight (float): The weight of the assignment as a percentage or fraction.
    """

    subject_assessment: str
    weighted_mark: Union[float, str] = 0.0  # float for numeric, str for "S"/"U"
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: Literal["numeric", "S", "U"] = "numeric"


@dataclass
class Examination:
    """
    Represents an examination with a mark and weight.
    Args:
        exam_mark (float): The mark obtained in the examination. Defaults to 0.0.
        exam_weight (float): The weight of the examination in percentage. Defaults to 100.0.
    """

    exam_mark: float = 0.0
    exam_weight: float = 100.0


@dataclass
class Subject:
    """
    Subject class represents an academic subject with its associated details.
    Attributes:
        subject_code (str): The unique code identifying the subject.
        subject_name (str): The name of the subject.
        assignments (List[Assignment]): A list of assignments associated with the subject.
        examinations (Examination): The examination details for the subject.
        sync_subject (bool): Indicates whether the subject is synchronized with an external system.
        total_mark (float): The total mark achieved in the subject.
    """

    subject_code: str
    subject_name: str
    assignments: List[Assignment] = field(default_factory=list)
    examinations: Examination = field(default_factory=Examination)
    sync_subject: bool = False
    total_mark: float = 0.0
