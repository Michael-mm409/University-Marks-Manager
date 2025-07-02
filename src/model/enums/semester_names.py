from enum import Enum


class SemesterName(str, Enum):
    AUTUMN = "Autumn"
    SPRING = "Spring"
    ANNUAL = "Annual"
    SUMMER = "Summer"
