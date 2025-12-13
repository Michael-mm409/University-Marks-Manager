-- Migration 001: Add unique constraint on subjects (subject_code, semester_name, year)
-- Pre-check: ensure no duplicates exist.
-- Run this SELECT; if it returns rows, fix them manually before applying the constraint.
-- SELECT subject_code, semester_name, year, COUNT(*)
-- FROM subjects
-- GROUP BY subject_code, semester_name, year
-- HAVING COUNT(*) > 1;

ALTER TABLE subjects
ADD CONSTRAINT uq_subject_code_semester_year
UNIQUE (subject_code, semester_name, year);
