from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union


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

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the instance attributes to a dictionary representation.
        Returns:
            Dict[str, Any]: A dictionary containing the following key-value pairs:
                - "subject_assessment": The subject assessment details.
                - "weighted_mark": The weighted mark of the assessment.
                - "unweighted_mark": The unweighted mark of the assessment.
                - "mark_weight": The weight of the mark in the overall grade.
                - "grade_type": The type of grade associated with the assessment.
        """

        return {
            "subject_assessment": self.subject_assessment,
            "weighted_mark": self.weighted_mark,
            "unweighted_mark": self.unweighted_mark,
            "mark_weight": self.mark_weight,
            "grade_type": self.grade_type,
        }


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

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the instance attributes to a dictionary representation.
        Returns:
            Dict[str, Any]: A dictionary containing the exam mark and exam weight
            with their corresponding values.
        """

        return {
            "exam_mark": self.exam_mark,
            "exam_weight": self.exam_weight,
        }


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

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Subject instance into a dictionary representation.
        """
        return {
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "assignments": [assignment.to_dict() for assignment in self.assignments],
            "total_mark": self.total_mark,
            "examinations": self.examinations.to_dict() if hasattr(self.examinations, "to_dict") else {},
            "sync_subject": self.sync_subject,
        }
