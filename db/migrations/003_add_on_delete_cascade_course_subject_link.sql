-- Migration 003: Add ON DELETE CASCADE to course_subject_link foreign keys.
-- This allows automatic cleanup of link rows when a Course or Subject is deleted.
-- Strategy: drop existing FK constraints and recreate with ON DELETE CASCADE.

-- Check current constraints (names may vary):
-- \d course_subject_link  (in psql)

ALTER TABLE course_subject_link DROP CONSTRAINT IF EXISTS course_subject_link_course_id_fkey;
ALTER TABLE course_subject_link DROP CONSTRAINT IF EXISTS course_subject_link_subject_id_fkey;

ALTER TABLE course_subject_link
ADD CONSTRAINT course_subject_link_course_id_fkey
FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE;

ALTER TABLE course_subject_link
ADD CONSTRAINT course_subject_link_subject_id_fkey
FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE;
