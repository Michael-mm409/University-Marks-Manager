from enum import Enum


class GradeType(str, Enum):
    """
    An enumeration representing different types of grades.

    Attributes:
        NUMERIC (str): Represents a numeric grade type.
        SATISFACTORY (str): Represents a satisfactory grade, denoted by "S".
        UNSATISFACTORY (str): Represents an unsatisfactory grade, denoted by "U".
    """

    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"
