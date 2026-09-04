-- Migration: Change grading_scale column in courses table from integer to text
ALTER TABLE courses
    ALTER COLUMN grading_scale TYPE text;
