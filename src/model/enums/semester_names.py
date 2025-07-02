from enum import Enum


class SemesterName(str, Enum):
    """
    An enumeration representing the names of academic semesters.

    Attributes:
        AUTUMN (str): Represents the Autumn semester.
        SPRING (str): Represents the Spring semester.
        ANNUAL (str): Represents the Annual semester, typically spanning the entire academic year.
        SUMMER (str): Represents the Summer semester.
    """

    AUTUMN = "Autumn"
    SPRING = "Spring"
    ANNUAL = "Annual"
    SUMMER = "Summer"
