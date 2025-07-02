from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator

from ...enums.grade_types import GradeType


class Assignment(BaseModel):
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
    mark_weight: Optional[float] = Field(default=None, ge=0.0, le=100.0)  # 0 - 100%
    grade_type: GradeType = GradeType.NUMERIC

    @field_validator("weighted_mark")
    @classmethod
    def validate_mark_weight(cls, value: Union[float, str]) -> Union[float, str]:
        """
        Validates the weighted mark to ensure it is either a float or a string.
        If the value is a string, it should be either "S" or "U".
        Args:
            value (Union[float, str]): The weighted mark to validate.
        Returns:
            Union[float, str]: The validated weighted mark.
        Raises:
            ValueError: If the value is not a float or not one of the allowed strings.
        """
        if isinstance(value, str) and value not in [GradeType.SATISFACTORY, GradeType.UNSATISFACTORY]:
            raise ValueError(
                f"Weighted mark must be '{GradeType.SATISFACTORY}', '{GradeType.UNSATISFACTORY}', or a numeric value."
            )
        return value

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
