"""SQLModel ORM models (infrastructure layer)."""
from __future__ import annotations

from enum import Enum
from typing import ClassVar, Optional

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

class GradeType(str, Enum):
    """Supported grading modes for an assessment component."""
    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"
    HIGH_DISTINCTION = "HD"
    DISTINCTION = "D"
    CREDIT = "C"
    PASS = "P"
    PASS_SUPPLEMENTARY = "PS"
    FAIL = "F"

class User(SQLModel, table=True):
    """Represents a user of the Marks Manager system."""
    __tablename__: ClassVar[str] = "users"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password_hash: str  # Store hashed password, never plain text
    
    user_courses: list["UserCourse"] = Relationship(
        sa_relationship=relationship("UserCourse", back_populates="user")
    )

class UserCourse(SQLModel, table=True):
    """Association table linking users to their courses."""
    __tablename__: ClassVar[str] = "user_courses"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    course_id: int = Field(foreign_key="courses.id", ondelete="CASCADE")
    is_default: bool = Field(default=False)  # User's default/active course
    
    user: Optional["User"] = Relationship(
        sa_relationship=relationship("User", back_populates="user_courses")
    )
    course: Optional["Course"] = Relationship(
        sa_relationship=relationship("Course")
    )
    
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )

class University(SQLModel, table=True):
    """Represents a university."""
    __tablename__: ClassVar[str] = "university"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
    courses: list["Course"] = Relationship(
        sa_relationship=relationship("Course", back_populates="university")
    )

class Course(SQLModel, table=True):
    """Represents a degree or program of study."""
    __tablename__: ClassVar[str] = "courses"  # type: ignore[assignment]
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
    __tablename__: ClassVar[str] = "semesters"  # type: ignore[assignment]
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
    __tablename__: ClassVar[str] = "subjects"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    semester_id: int = Field(foreign_key="semesters.id", index=True)
    subject_name: str
    total_mark: Optional[float] = 0.0
    credit_points: int = Field(default=6)
    sync_subject: bool = False
    has_exam: bool = Field(default=True)

    # Relationship to Semester
    semester: Optional["Semester"] = Relationship(
        sa_relationship=relationship("Semester", back_populates="subjects")
    )

    # Relationship to Assignment
    assignments: list["Assignment"] = Relationship(
        sa_relationship=relationship("Assignment", back_populates="subject")
    )

    # Relationship to SubjectRule
    rules: list["SubjectRule"] = Relationship(
        sa_relationship=relationship("SubjectRule", back_populates="subject")
    )

    # Prerequisites: subjects this subject requires
    prerequisites: list["SubjectPrerequisite"] = Relationship(
        sa_relationship=relationship(
            "SubjectPrerequisite",
            back_populates="subject",
            primaryjoin="Subject.id==SubjectPrerequisite.subject_id",
            cascade="all, delete-orphan"
        )
    )
    # Subjects for which this subject is a prerequisite
    required_for: list["SubjectPrerequisite"] = Relationship(
        sa_relationship=relationship(
            "SubjectPrerequisite",
            back_populates="prerequisite_subject",
            primaryjoin="Subject.id==SubjectPrerequisite.prerequisite_subject_id",
            cascade="all, delete-orphan"
        )
    )

    __table_args__ = (
        UniqueConstraint("subject_code", "semester_id", name="uq_subject_code_semester"),
    )


# New model for subject prerequisites
class SubjectPrerequisite(SQLModel, table=True):
    __tablename__: ClassVar[str] = "subject_prerequisite"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True)
    # Either link to another subject (prerequisite_subject_id) or store free-text in custom_text
    prerequisite_subject_id: Optional[int] = Field(
        default=None, foreign_key="subjects.id", index=True
    )
    custom_text: Optional[str] = None
    is_corequisite: bool = Field(default=False, nullable=False)

    subject: Optional["Subject"] = Relationship(
        sa_relationship=relationship(
            "Subject",
            foreign_keys="SubjectPrerequisite.subject_id",
            back_populates="prerequisites"
        )
    )
    prerequisite_subject: Optional["Subject"] = Relationship(
        sa_relationship=relationship(
            "Subject",
            foreign_keys="SubjectPrerequisite.prerequisite_subject_id",
            back_populates="required_for"
        )
    )

class Assignment(SQLModel, table=True):
    __tablename__: ClassVar[str] = "assignments"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    assessment: str = Field(index=True)
    category: Optional[str] = Field(default=None, index=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True)
    weighted_mark: Optional[float] = Field(default=None, nullable=True)
    unweighted_mark: Optional[float] = Field(default=None, nullable=True)
    mark_weight: Optional[float] = None
    grade_type: str = Field(default=GradeType.NUMERIC.value)
    is_exam: bool = Field(default=False)
    
    subject: Optional["Subject"] = Relationship(
        sa_relationship=relationship("Subject", back_populates="assignments")
    )
    
    __table_args__ = (
        UniqueConstraint("assessment", "subject_id", name="uq_assignment_subject"),
    )

class Examination(SQLModel, table=True):
    __tablename__: ClassVar[str] = "examinations"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True, unique=True)
    exam_mark: float = 0
    exam_weight: float = 100
    exam_type: str = Field(default="main", max_length=32, description="Type of exam, e.g., 'assignment', 'main', etc.")

class ExamSettings(SQLModel, table=True):
    __tablename__: ClassVar[str] = "exam_settings"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True, unique=True)
    ps_exam: bool = False
    ps_factor: float = 40.0

class GradeScale(SQLModel, table=True):
    __tablename__: ClassVar[str] = "grade_scales"  # type: ignore[assignment]
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

# New model for subject prerequisites and rules
class SubjectRule(SQLModel, table=True):
    __tablename__: ClassVar[str] = "subject_rules"  # type: ignore[assignment]
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True)
    rule_label: str
    sql_pattern: str
    max_count: int = 9
    weight_each: float = 2.0
    
    subject: Optional["Subject"] = Relationship(
        sa_relationship=relationship("Subject", back_populates="rules")
    )

# Required for SQLModel to handle circular imports and forward references
University.model_rebuild()
Course.model_rebuild()
Semester.model_rebuild()
Subject.model_rebuild()
SubjectPrerequisite.model_rebuild()
Assignment.model_rebuild()
SubjectRule.model_rebuild()

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