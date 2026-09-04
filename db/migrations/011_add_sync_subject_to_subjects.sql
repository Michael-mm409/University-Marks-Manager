-- Migration: Add sync_subject column to subjects table
ALTER TABLE subjects ADD COLUMN sync_subject BOOLEAN NOT NULL DEFAULT FALSE;