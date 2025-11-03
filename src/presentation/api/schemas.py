from typing import Optional

from sqlmodel import SQLModel


class SubjectCreate(SQLModel, table=False):
    subject_code: str
    subject_name: str
    semester_name: str
    year: str
    sync_subject: bool = False
    total_mark: Optional[float] = None


class SubjectRead(SQLModel):
    subject_code: str
    subject_name: str
    semester_name: str
    year: str
    sync_subject: bool
    total_mark: Optional[float] = None

    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]


class AssignmentCreate(SQLModel, table=False):
    assessment: str
    subject_code: str
    semester_name: str
    year: str
    weighted_mark: Optional[float] = None
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str = "numeric"


class AssignmentRead(SQLModel):
    assessment: str
    subject_code: str
    semester_name: str
    year: str
    weighted_mark: Optional[float] = None
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str

    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]


class ExaminationCreate(SQLModel, table=False):
    subject_code: str
    semester_name: str
    year: str
    exam_mark: Optional[float] = None
    exam_weight: Optional[float] = None


class ExaminationRead(SQLModel):
    subject_code: str
    semester_name: str
    year: str
    exam_mark: float
    exam_weight: float

    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]


class SemesterCreate(SQLModel, table=False):
    name: str
    year: int


class SemesterRead(SQLModel):
    name: str
    year: int
    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]
