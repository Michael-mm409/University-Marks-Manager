-- Migration: Add surrogate ID primary keys to Examination and ExamSettings
--
-- STRATEGY:
-- Replace natural key PRIMARY KEYs (subject_code, semester_name, year) with surrogate id columns.
-- This prepares for removing denormalized columns while maintaining referential integrity.
--
-- TABLES AFFECTED:
-- - examinations: Add id column, make it PRIMARY KEY, keep natural key as UNIQUE
-- - exam_settings: Add id column, make it PRIMARY KEY, keep natural key as UNIQUE
--
-- NOTE: This migration does NOT remove denormalized columns yet. That will happen in migration 007
-- after we verify the new structure works correctly.

BEGIN;

-- ============================================================================
-- STEP 1: examinations table - Add surrogate ID
-- ============================================================================

-- Add id column (will be auto-incrementing)
ALTER TABLE examinations ADD COLUMN id SERIAL;

-- Drop existing PRIMARY KEY constraint on natural key
ALTER TABLE examinations DROP CONSTRAINT IF EXISTS examinations_pkey;

-- Make id the new PRIMARY KEY
ALTER TABLE examinations ADD CONSTRAINT examinations_pkey PRIMARY KEY (id);

-- Add UNIQUE constraint on natural key to maintain uniqueness
ALTER TABLE examinations ADD CONSTRAINT uq_examination_natural_key 
    UNIQUE (subject_code, semester_name, year);

-- Make subject_id NOT NULL (it should already be populated from migration 002)
ALTER TABLE examinations ALTER COLUMN subject_id SET NOT NULL;


-- ============================================================================
-- STEP 2: exam_settings table - Add surrogate ID
-- ============================================================================

-- Add id column (will be auto-incrementing)
ALTER TABLE exam_settings ADD COLUMN id SERIAL;

-- Drop existing PRIMARY KEY constraint on natural key
ALTER TABLE exam_settings DROP CONSTRAINT IF EXISTS exam_settings_pkey;

-- Make id the new PRIMARY KEY
ALTER TABLE exam_settings ADD CONSTRAINT exam_settings_pkey PRIMARY KEY (id);

-- Add UNIQUE constraint on natural key to maintain uniqueness
ALTER TABLE exam_settings ADD CONSTRAINT uq_exam_settings_natural_key 
    UNIQUE (subject_code, semester_name, year);

-- Make subject_id NOT NULL (it should already be populated from migration 002)
ALTER TABLE exam_settings ALTER COLUMN subject_id SET NOT NULL;


-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- Check PRIMARY KEYs are now on id columns:
-- SELECT conname, contype, conrelid::regclass 
-- FROM pg_constraint 
-- WHERE conrelid IN ('examinations'::regclass, 'exam_settings'::regclass) 
-- AND contype = 'p';
--
-- Check UNIQUE constraints exist on natural keys:
-- SELECT conname, contype, conrelid::regclass 
-- FROM pg_constraint 
-- WHERE conrelid IN ('examinations'::regclass, 'exam_settings'::regclass) 
-- AND contype = 'u';

COMMIT;
