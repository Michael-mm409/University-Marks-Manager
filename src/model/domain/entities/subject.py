from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .assignment import Assignment
from .examination import Examination


class Subject(BaseModel):
    """
    Subject class represents an academic subject with its associated details.
    Args:
        subject_code (str): The unique code identifying the subject.
        subject_name (str): The name of the subject.
        assignments (List[Assignment]): A list of assignments associated with the subject.
        examinations (Examination): The examination details for the subject.
        sync_subject (bool): Indicates whether the subject is synchronized with an external system.
        total_mark (float): The total mark achieved in the subject.
    """

    subject_code: str
    subject_name: str
    assignments: List[Assignment] = Field(default_factory=list)
    examinations: Examination = Field(default_factory=Examination)
    sync_subject: bool = False
    total_mark: float = Field(default=0.0, ge=0.0, le=100.0)  # 0 - 100%

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
