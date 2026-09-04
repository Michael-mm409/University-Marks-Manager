-- Migration: Add exam_type column to examinations table
-- Allows distinguishing between assignments, main exams, etc.

ALTER TABLE examinations ADD COLUMN exam_type VARCHAR(32) DEFAULT 'main';

-- Optionally, update existing rows if you want to set a different type for some exams:
-- UPDATE examinations SET exam_type = 'assignment' WHERE ...;
