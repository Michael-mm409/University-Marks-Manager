# Data Model Overview (current vs target)

This document reconciles the current application schema with the target UML (normalized with surrogate keys) and outlines a staged migration plan.

![Relational Diagram](../UML/relational%20diagram.png)

## Target schema (UML)

The UML describes the desired normalized model:

- Course(id, code UNIQUE, name)
- Semester(id PK, name, year, course_id FK Course(id), UNIQUE(course_id, name, year))
- Subject(id PK, subject_code, subject_name, semester_id FK Semester(id), total_mark, sync_subject, UNIQUE(semester_id, subject_code))
- Assignment(id PK, subject_id FK Subject(id), assessment, weighted_mark, unweighted_mark, mark_weight, grade_type, UNIQUE(subject_id, assessment))
- Examination(subject_id PK/FK Subject(id), exam_mark, exam_weight) 1:1 with Subject
- ExamSettings(subject_id PK/FK Subject(id), ps_exam, ps_factor) 1:1 with Subject

Rationale:

- Surrogate integer keys and proper FKs avoid string-mismatch bugs and simplify joins.
- Uniques enforce business rules at the DB layer (e.g., one subject_code per semester, one exam per subject).

## Current application schema (as implemented)

Today, the code primarily uses natural keys and composites:

- Semester: id PK (present), name TEXT, year INT, course_id FK; UNIQUE(name, year) in DB (to be aligned to UNIQUE(course_id, name, year)).
- Subject: id PK, subject_code TEXT, subject_name TEXT, semester_name TEXT, year TEXT, total_mark REAL, sync_subject BOOL.
- Assignment: id PK, assessment TEXT, subject_code TEXT, semester_name TEXT, year TEXT, weighted_mark REAL, unweighted_mark REAL, mark_weight REAL, grade_type TEXT; UNIQUE(assessment, subject_code, semester_name, year).
- Examination: composite PK (subject_code, semester_name, year).
- ExamSettings: composite PK (subject_code, semester_name, year).
- Course: id PK, code UNIQUE, name (plus a many-to-many Course↔Subject link table used for filtering).

Implications:

- Subjects and children (Assignment, Examination, ExamSettings) are joined by (subject_code, semester_name, year) rather than subject_id.
- Semester uniqueness currently ignores course_id; duplicates across courses are theoretically blocked (will be fixed during migration).

## Migration plan (staged and backward compatible)

Stage 1: Constraints and compatibility columns

- Enforce Semester uniqueness per UML at the model level: UNIQUE(course_id, name, year). A DB migration is required to update the constraint.
- Keep existing Subject fields (semester_name, year) but introduce and backfill semester_id via join on (name, year, course_id).
- Introduce and backfill subject_id on Assignment, Examination, ExamSettings via join from Subject (subject_code, semester_name, year).
- Maintain legacy fields during the transition; code continues to function.

Stage 2: Code refactor to IDs

- Update queries and routes to prefer subject_id/semester_id internally (pretty URLs can remain name/code based, resolved at request-time).
- Remove reliance on the Course↔Subject link if not needed; or document it in UML if it’s a required feature.

Stage 3: Cleanup

- Drop legacy composite columns and constraints after the switch to ID-based logic is complete and data is verified.

## Status today

- The application code and DB still operate on the current schema.
- The model definition for Semester now targets UNIQUE(course_id, name, year) and needs a DB migration to enforce.

If you want, we can add migration scripts to backfill new FK columns and adjust constraints with minimal downtime.
