from typing import Any, Dict

from pydantic import BaseModel, Field


class Examination(BaseModel):
    """
    Represents an examination with a mark and weight.
    Args:
        exam_mark (float): The mark obtained in the examination. Defaults to 0.0.
        exam_weight (float): The weight of the examination in percentage. Defaults to 100.0.
    """

    exam_mark: float = Field(default=0.0, ge=0.0, le=100.0)  # 0 - 100%
    exam_weight: float = Field(default=100.0, ge=0.0, le=100.0)  # 0 - 100%

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the instance Args to a dictionary representation.
        Returns:
            Dict[str, Any]: A dictionary containing the exam mark and exam weight
            with their corresponding values.
        """

        return {
            "exam_mark": self.exam_mark,
            "exam_weight": self.exam_weight,
        }
