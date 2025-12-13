from typing import Optional

from sqlmodel import SQLModel


# Normalized API schemas: use foreign key IDs explicitly.
class SubjectCreate(SQLModel, table=False):
    subject_code: str
    subject_name: str
    semester_id: int  # FK to Semester(id)
    total_mark: Optional[float] = None


class SubjectRead(SQLModel):
    id: int
    subject_code: str
    subject_name: str
    semester_id: int
    # sync_subject removed
    total_mark: Optional[float] = None
    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]


class AssignmentCreate(SQLModel, table=False):
    assessment: str
    subject_id: int  # FK to Subject(id)
    weighted_mark: Optional[float] = None
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str = "numeric"
    # denormalized fields removed


class AssignmentRead(SQLModel):
    id: int
    assessment: str
    subject_id: int
    weighted_mark: Optional[float] = None
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str
    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]


class ExaminationCreate(SQLModel, table=False):
    subject_id: int  # FK to Subject(id)
    exam_mark: Optional[float] = None
    exam_weight: Optional[float] = None
    # denormalized fields removed


class ExaminationRead(SQLModel):
    id: int
    subject_id: int
    exam_mark: float
    exam_weight: float
    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]


class SemesterCreate(SQLModel, table=False):
    name: str
    year: int


class SemesterRead(SQLModel):
    id: int
    name: str
    year: int
    # pydantic v2: enable attribute population from ORM objects
    model_config = {"from_attributes": True}  # type: ignore[assignment]
