-- Migration: Allow custom text prerequisites
ALTER TABLE subject_prerequisite
    ADD COLUMN custom_text TEXT,
    ALTER COLUMN prerequisite_subject_id DROP NOT NULL;
