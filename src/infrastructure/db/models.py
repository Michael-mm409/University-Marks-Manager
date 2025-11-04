"""SQLModel ORM models (infrastructure layer)."""
from __future__ import annotations

from enum import Enum
from typing import ClassVar, Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship as sa_relationship


class GradeType(str, Enum):
    """Supported grading modes for an assessment component."""

    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"


class CourseSubjectLink(SQLModel, table=True):
    """Link table for the many-to-many relationship between Course and Subject."""

    __tablename__: ClassVar[str] = "course_subject_link"
    course_id: Optional[int] = Field(
        default=None, foreign_key="courses.id", primary_key=True
    )
    subject_id: Optional[int] = Field(
        default=None, foreign_key="subjects.id", primary_key=True
    )
    # NOTE: Consider adding DB-level ON DELETE CASCADE on both foreign keys via a migration
    # so that removing a Course or Subject cleans up association rows automatically.
    

class Semester(SQLModel, table=True):
    """Academic semester (e.g., Autumn 2025)."""

    __tablename__: ClassVar[str] = "semesters"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: int = Field(index=True)
    course_id: Optional[int] = Field(default=None, foreign_key="courses.id")
    __table_args__ = (
        UniqueConstraint("name", "year", name="uq_semester_name_year"),
    )

    # Relationship is attached after class definitions to avoid forward-ref issues
    # course: "Course" = Relationship(back_populates="semesters")


class Subject(SQLModel, table=True):
    """Subject/course within a semester/year."""

    __tablename__: ClassVar[str] = "subjects"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    semester_name: str = Field(index=True)
    year: str = Field(index=True)
    subject_name: str
    total_mark: Optional[float] = 0.0
    sync_subject: bool = False

    # NOTE:
    # 1) The (subject_code, semester_name, year) triple behaves like a natural key across the app.
    #    Consider adding a UniqueConstraint on these three columns in a schema migration to prevent duplicates.
    # 2) `year` here (and in related tables) is typed as str whereas `Semester.year` is int.
    #    Aligning these to int would reduce subtle bugs but requires a data migration.

    # Define many-to-many only on Course side to avoid forward-ref generic issues here
    # If needed later, reintroduce with list[Course] once mapping is stable
    # courses: list["Course"] = Relationship(back_populates="subjects", link_model=CourseSubjectLink)


class Course(SQLModel, table=True):
    """Represents a degree or program of study."""

    __tablename__: ClassVar[str] = "courses"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(index=True)
    __table_args__ = (
        UniqueConstraint("code", name="uq_course_code"),
        UniqueConstraint("name", "code", name="uq_course_name_code"),
    )

    # NOTE: The unique constraint on (name, code) is redundant if `code` is globally unique.
    # It can be dropped in a future migration to simplify the schema.

    # Relationships are attached after class definitions to avoid forward-ref issues
    # semesters: list[Semester] = Relationship(back_populates="course")
    # subjects: list[Subject] = Relationship(back_populates="courses", link_model=CourseSubjectLink)


class Assignment(SQLModel, table=True):
    """Assessment item belonging to a subject (numeric or S/U)."""

    __tablename__: ClassVar[str] = "assignments"
    id: Optional[int] = Field(default=None, primary_key=True)
    assessment: str = Field(index=True)
    subject_code: str = Field(index=True)
    semester_name: str = Field(index=True)
    year: str = Field(index=True)
    # Store numeric weighted marks as floats. Grade type tracks S/U separately.
    weighted_mark: Optional[float] = None
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str = Field(default=GradeType.NUMERIC.value)
    __table_args__ = (
        UniqueConstraint("assessment", "subject_code", "semester_name", "year", name="uq_assignment"),
    )


class Examination(SQLModel, table=True):
    """Single exam record per subject."""

    __tablename__: ClassVar[str] = "examinations"
    subject_code: str = Field(primary_key=True, index=True)
    semester_name: str = Field(primary_key=True, index=True)
    year: str = Field(primary_key=True, index=True)
    exam_mark: float = 0
    exam_weight: float = 100


class ExamSettings(SQLModel, table=True):
    """
    Stores pass-scale (PS) exam configuration separately to avoid altering existing tables.

    This allows persisting ps_exam flag and ps_factor without a migration altering the Examination table already present in user data.
    """

    __tablename__: ClassVar[str] = "exam_settings"
    subject_code: str = Field(primary_key=True, index=True)
    semester_name: str = Field(primary_key=True, index=True)
    year: str = Field(primary_key=True, index=True)
    ps_exam: bool = False
    ps_factor: float = 40.0


__all__ = [
	"GradeType",
	"Semester",
	"Subject",
	"Assignment",
	"Examination",
    "ExamSettings",
    "Course",
    "CourseSubjectLink",
]

# Attach relationships explicitly after all classes are defined to avoid
# SQLAlchemy trying to resolve generic strings like "Optional['Course']" or "list['Semester']".
Semester.course = sa_relationship("Course", back_populates="semesters")
Course.semesters = sa_relationship("Semester", back_populates="course")
# Many-to-many: expose a bidirectional convenience relationship between Course and Subject via link table
Course.subjects = sa_relationship("Subject", secondary="course_subject_link", back_populates="courses")
Subject.courses = sa_relationship("Course", secondary="course_subject_link", back_populates="subjects")

# Manually update forward references to resolve circular dependencies
Course.model_rebuild()
Semester.model_rebuild()
Subject.model_rebuild()

