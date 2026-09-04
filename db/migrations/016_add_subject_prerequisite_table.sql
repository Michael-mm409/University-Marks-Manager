-- Migration: Add subject_prerequisite table for subject prerequisites
CREATE TABLE subject_prerequisite (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    prerequisite_subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    CONSTRAINT uq_subject_prerequisite UNIQUE (subject_id, prerequisite_subject_id)
);
