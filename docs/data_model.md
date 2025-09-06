# Data Model Overview

This document describes the data model for the University Marks Manager, aligning the UML diagram with the actual SQLite schema.

![Relational Diagram](../UML/relational%20diagram.bmp)
## Tables and Relationships

### Semester
- **Fields:**
  - `name`: TEXT (PK)
  - `year`: TEXT (PK)
- **Notes:**
  - The primary key is a composite of `name` and `year`.
  - No separate `id` field is present in the schema.

### Subjects
- **Fields:**
  - `subject_code`: (PK)
  - `subject_name`: (PK)
  - `semester_name`: TEXT (FK to Semester.name) (PK)
  - `year`: TEXT
  - `total_mark`: REAL DEFAULT 0.0
  - `sync_subject`: BOOLEAN (INTEGER 0/1)
- **Constraints:**
  - Foreign key (`semester_name`, `year`) references Semester(`name`, `year`).

### Assignment
- **Fields:**
  - `subject_code`: TEXT (NOT NULL) (PK)
  - `semester_name`: TEXT (PK)
  - `year`: TEXT  (PK)
  - `assessment`: TEXT (PK)
  - `weighted_mark`: REAL
  - `unweighted_mark`: REAL
  - `mark_weight`: REAL
  - `grade_type`: TEXT (enum)
- **Constraints:**
  - UNIQUE(`assessment`, `subject_code`, `semester_name`, `year`)
  - Foreign key (`subject_code`, `semester_name`, `year`) references Subjects(`subject_code`, `semester_name`, `year`).
  - `grade_type` should be validated as an enum (use CHECK or a lookup table if needed).

### Examination
- **Fields:**
  - `subject_code`: TEXT  (PK)
  - `semester_name`: TEXT  (PK)
  - `year`: TEXT   (PK)
  - `exam_mark`: REAL
  - `exam_weight`: REAL
- **Constraints:**
  - UNIQUE(`subject_code`, `semester_name`, `year`)
  - Foreign key (`subject_code`, `semester_name`, `year`) references Subjects(`subject_code`, `semester_name`, `year`).

### ExamSettings
- **Fields:**
  - `subject_code`: TEXT  (PK)
  - `semester_name`: TEXT  (PK)
  - `year`: TEXT (PK)
  - `ps_exam`: BOOLEAN (INTEGER 0/1)
  - `ps_factor`: REAL

## Data Types and Conventions
- **Booleans:** Stored as INTEGER (0/1) in SQLite.
- **Enums:** Use TEXT with CHECK constraints or a lookup table for validation.
- **Foreign Keys:** All relationships are enforced for referential integrity.
- **Defaults:** `total_mark` defaults to 0.0.

## Summary of Alignment
- The model now matches the schema:
  - Composite PKs and FKs are used as in the database.
  - Data types reflect SQLite conventions.
  - Constraints (UNIQUE, FK, enum/boolean) are enforced.

For further details, see the UML diagram and the actual SQLite schema in `data/marks.db`.
