-- Migration 008: Drop course_subject_link table
-- 
-- Rationale: The direct many-to-many relationship between Course and Subject is redundant.
-- The proper hierarchy is: Course -> Semester -> Subject
-- Subjects are implicitly associated with courses through their semester's course_id.
--
-- This migration removes the link table and its constraints.

-- Drop the course_subject_link table
DROP TABLE IF EXISTS course_subject_link;
