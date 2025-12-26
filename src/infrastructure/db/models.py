"""SQLModel ORM models (infrastructure layer)."""
from __future__ import annotations

from enum import Enum
from typing import ClassVar, Optional, List

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

class GradeType(str, Enum):
    """Supported grading modes for an assessment component."""
    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"

class University(SQLModel, table=True):
    """Represents a university."""
    __tablename__: ClassVar[str] = "university"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
    courses: list["Course"] = Relationship(
        sa_relationship=relationship("Course", back_populates="university")
    )

class Course(SQLModel, table=True):
    """Represents a degree or program of study."""
    __tablename__: ClassVar[str] = "courses"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(index=True)
    grading_scale_id: int = Field(foreign_key="grade_scales.id")
    university_id: Optional[int] = Field(default=None, foreign_key="university.id")
    
    university: Optional["University"] = Relationship(
        sa_relationship=relationship("University", back_populates="courses")
    )
    grading_scale: Optional["GradeScale"] = Relationship(
        sa_relationship=relationship("GradeScale")
    )
    # This points to Semester.course
    semesters: list["Semester"] = Relationship(
        sa_relationship=relationship("Semester", back_populates="course")
    )
    
    __table_args__ = (
        UniqueConstraint("code", name="uq_course_code"),
    )

class Semester(SQLModel, table=True):
    """Academic semester (e.g., Autumn 2025)."""
    __tablename__: ClassVar[str] = "semesters"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: int = Field(index=True)
    course_id: Optional[int] = Field(default=None, foreign_key="courses.id")
    
    # FIXED: Added the missing relationship side for Course
    course: Optional["Course"] = Relationship(
        sa_relationship=relationship("Course", back_populates="semesters")
    )
    # FIXED: Added the missing relationship side for Subject
    subjects: list["Subject"] = Relationship(
        sa_relationship=relationship("Subject", back_populates="semester")
    )

    __table_args__ = (
        UniqueConstraint("course_id", "name", "year", name="uq_semester_course_name_year"),
    )

class Subject(SQLModel, table=True):
    """Subject/course within a semester."""
    __tablename__: ClassVar[str] = "subjects"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    semester_id: int = Field(foreign_key="semesters.id", index=True)
    subject_name: str
    total_mark: Optional[float] = 0.0
    credit_points: int = Field(default=6)
    sync_subject: bool = False
    has_exam: bool = Field(default=True)

    # FIXED: Added the missing relationship side for Semester
    semester: Optional["Semester"] = Relationship(
        sa_relationship=relationship("Semester", back_populates="subjects")
    )

    __table_args__ = (
        UniqueConstraint("subject_code", "semester_id", name="uq_subject_code_semester"),
    )

class Assignment(SQLModel, table=True):
    __tablename__: ClassVar[str] = "assignments"
    id: Optional[int] = Field(default=None, primary_key=True)
    assessment: str = Field(index=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True)
    weighted_mark: Optional[float] = None
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str = Field(default=GradeType.NUMERIC.value)
    is_exam: bool = Field(default=False)
    __table_args__ = (
        UniqueConstraint("assessment", "subject_id", name="uq_assignment_subject"),
    )

class Examination(SQLModel, table=True):
    __tablename__: ClassVar[str] = "examinations"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True, unique=True)
    exam_mark: float = 0
    exam_weight: float = 100

class ExamSettings(SQLModel, table=True):
    __tablename__: ClassVar[str] = "exam_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True, unique=True)
    ps_exam: bool = False
    ps_factor: float = 40.0

class GradeScale(SQLModel, table=True):
    __tablename__: ClassVar[str] = "grade_scales"
    id: Optional[int] = Field(default=None, primary_key=True)
    scale_name: str = Field(default="Standard", index=True)
    grade: str
    label: str
    min_mark: float
    gpa_point: float
    band_type: str = Field(default="both", index=True)
    __table_args__ = (
        UniqueConstraint("scale_name", "grade", "band_type", name="uq_scale_grade_type"),
    )

# Required for SQLModel to handle circular imports and forward references
University.model_rebuild()
Course.model_rebuild()
Semester.model_rebuild()
Subject.model_rebuild()

__all__ = [
    "GradeType",
    "Semester",
    "Subject",
    "Assignment",
    "Examination",
    "ExamSettings",
    "Course",
    "University",
    "GradeScale",
]