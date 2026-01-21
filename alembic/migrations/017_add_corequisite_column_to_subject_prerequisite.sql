-- Migration: Add is_corequisite column to subject_prerequisite
ALTER TABLE subject_prerequisite ADD COLUMN is_corequisite BOOLEAN NOT NULL DEFAULT FALSE;
