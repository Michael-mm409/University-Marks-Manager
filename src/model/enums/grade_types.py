from enum import Enum


class GradeType(str, Enum):
    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"
