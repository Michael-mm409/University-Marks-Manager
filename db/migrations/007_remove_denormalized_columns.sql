-- Migration: Remove denormalized columns from Assignment, Examination, ExamSettings
--
-- STRATEGY:
-- Now that we have:
-- - Normalized FKs (semester_id in Subject, subject_id in child tables)
-- - Surrogate ID PKs in Examination/ExamSettings (from migration 006)
-- We can safely remove the denormalized natural key columns.
--
-- TABLES AFFECTED:
-- - subjects: Remove semester_name, year (keep semester_id FK)
-- - assignments: Remove subject_code, semester_name, year (keep subject_id FK)
-- - examinations: Remove subject_code, semester_name, year (keep subject_id FK)
-- - exam_settings: Remove subject_code, semester_name, year (keep subject_id FK)
--
-- IMPORTANT: This is a BREAKING CHANGE for any application code that references these columns.
-- All queries must be updated to JOIN through FKs instead of using denormalized columns.

BEGIN;

-- ============================================================================
-- PRE-CHECK: Verify all FKs are populated and NOT NULL
-- ============================================================================
-- Uncomment to verify before running:
-- SELECT 
--     (SELECT COUNT(*) FROM subjects WHERE semester_id IS NULL) as subjects_null_semester_id,
--     (SELECT COUNT(*) FROM assignments WHERE subject_id IS NULL) as assignments_null_subject_id,
--     (SELECT COUNT(*) FROM examinations WHERE subject_id IS NULL) as examinations_null_subject_id,
--     (SELECT COUNT(*) FROM exam_settings WHERE subject_id IS NULL) as exam_settings_null_subject_id;
-- Expected: All counts should be 0


-- ============================================================================
-- STEP 1: subjects table - Remove denormalized columns
-- ============================================================================

-- Drop unique constraint that references the columns we're about to remove
ALTER TABLE subjects DROP CONSTRAINT IF EXISTS uq_subject_code_semester_year;

-- Drop the denormalized columns
ALTER TABLE subjects DROP COLUMN IF EXISTS semester_name;
ALTER TABLE subjects DROP COLUMN IF EXISTS year;

-- Create new unique constraint using normalized FK: (subject_code, semester_id)
ALTER TABLE subjects ADD CONSTRAINT uq_subject_code_semester 
    UNIQUE (subject_code, semester_id);


-- ============================================================================
-- STEP 2: assignments table - Remove denormalized columns
-- ============================================================================

-- Drop unique constraint that references the columns we're about to remove
ALTER TABLE assignments DROP CONSTRAINT IF EXISTS uq_assignment;

-- Drop the denormalized columns
ALTER TABLE assignments DROP COLUMN IF EXISTS subject_code;
ALTER TABLE assignments DROP COLUMN IF EXISTS semester_name;
ALTER TABLE assignments DROP COLUMN IF EXISTS year;

-- Create new unique constraint using normalized FK: (assessment, subject_id)
ALTER TABLE assignments ADD CONSTRAINT uq_assignment_subject 
    UNIQUE (assessment, subject_id);


-- ============================================================================
-- STEP 3: examinations table - Remove denormalized columns
-- ============================================================================

-- Drop unique constraint on natural key (added in migration 006)
ALTER TABLE examinations DROP CONSTRAINT IF EXISTS uq_examination_natural_key;

-- Drop the denormalized columns
ALTER TABLE examinations DROP COLUMN IF EXISTS subject_code;
ALTER TABLE examinations DROP COLUMN IF EXISTS semester_name;
ALTER TABLE examinations DROP COLUMN IF EXISTS year;

-- Add unique constraint on subject_id (one exam per subject)
ALTER TABLE examinations ADD CONSTRAINT uq_examination_subject 
    UNIQUE (subject_id);


-- ============================================================================
-- STEP 4: exam_settings table - Remove denormalized columns
-- ============================================================================

-- Drop unique constraint on natural key (added in migration 006)
ALTER TABLE exam_settings DROP CONSTRAINT IF EXISTS uq_exam_settings_natural_key;

-- Drop the denormalized columns
ALTER TABLE exam_settings DROP COLUMN IF EXISTS subject_code;
ALTER TABLE exam_settings DROP COLUMN IF EXISTS semester_name;
ALTER TABLE exam_settings DROP COLUMN IF EXISTS year;

-- Add unique constraint on subject_id (one exam settings per subject)
ALTER TABLE exam_settings ADD CONSTRAINT uq_exam_settings_subject 
    UNIQUE (subject_id);


-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- Check that denormalized columns are gone:
-- SELECT table_name, column_name 
-- FROM information_schema.columns 
-- WHERE table_schema = 'public' 
-- AND column_name IN ('subject_code', 'semester_name', 'year')
-- AND table_name IN ('subjects', 'assignments', 'examinations', 'exam_settings')
-- ORDER BY table_name, column_name;
--
-- Expected: Only subjects.subject_code should remain (it's the actual subject identifier)
--
-- Check new unique constraints:
-- SELECT conname, conrelid::regclass 
-- FROM pg_constraint 
-- WHERE conname LIKE 'uq_%subject%' OR conname LIKE 'uq_%semester%'
-- ORDER BY conrelid::regclass::text, conname;

COMMIT;
