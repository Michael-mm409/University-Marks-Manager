from dataclasses import dataclass, field
from typing import List


@dataclass
class Assignment:
    """Represents an assignment with a name and a list of marks."""

    subject_assessment: str
    unweighted_mark: float
    weighted_mark: float
    mark_weight: float


@dataclass
class Examination:
    """Represents an examination with a mark and weight."""

    exam_mark: float = 0.0
    exam_weight: float = 100.0


@dataclass
class Subject:
    subject_code: str
    subject_name: str
    assignments: List[Assignment] = field(default_factory=list)
    examinations: Examination = field(default_factory=Examination)
    sync_subject: bool = False
    total_mark: float = 0.0
