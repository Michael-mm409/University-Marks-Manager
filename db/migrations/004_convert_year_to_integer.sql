-- Migration: Convert year columns from VARCHAR to INTEGER
-- This migration aligns year types across all tables to match Semester.year (int)
-- and eliminates type inconsistencies that can cause subtle bugs.
--
-- STRATEGY:
-- 1. Add new INTEGER columns with temporary names (_new suffix)
-- 2. Backfill new columns by casting VARCHAR to INTEGER
-- 3. Drop old VARCHAR columns
-- 4. Rename new columns to original names
-- 5. Recreate constraints and indexes that reference year
--
-- TABLES AFFECTED:
-- - subjects (year: VARCHAR → INTEGER)
-- - assignments (year: VARCHAR → INTEGER)
-- - examinations (year: VARCHAR → INTEGER, part of PRIMARY KEY)
-- - exam_settings (year: VARCHAR → INTEGER, part of PRIMARY KEY)
--
-- NOTE: Recreating PRIMARY KEYs on examinations and exam_settings is complex.
-- We'll need to drop and recreate them with INTEGER year column.

BEGIN;

-- ============================================================================
-- PRE-CHECK: Verify all year values are valid integers
-- ============================================================================
-- Uncomment to run pre-check manually:
-- SELECT 'subjects', subject_code, year FROM subjects WHERE year !~ '^[0-9]+$'
-- UNION ALL
-- SELECT 'assignments', assessment, year FROM assignments WHERE year !~ '^[0-9]+$'
-- UNION ALL
-- SELECT 'examinations', subject_code, year FROM examinations WHERE year !~ '^[0-9]+$'
-- UNION ALL
-- SELECT 'exam_settings', subject_code, year FROM exam_settings WHERE year !~ '^[0-9]+$';
-- Expected: 0 rows (all years should be numeric strings like '2024', '2025')


-- ============================================================================
-- STEP 1: subjects table
-- ============================================================================
-- Add temporary INTEGER column
ALTER TABLE subjects ADD COLUMN year_new INTEGER;

-- Backfill from VARCHAR to INTEGER
UPDATE subjects SET year_new = year::INTEGER;

-- Make NOT NULL after backfill
ALTER TABLE subjects ALTER COLUMN year_new SET NOT NULL;

-- Drop the unique constraint that references the old year column
ALTER TABLE subjects DROP CONSTRAINT IF EXISTS uq_subject_code_semester_year;

-- Drop the old VARCHAR column
ALTER TABLE subjects DROP COLUMN year;

-- Rename new column to original name
ALTER TABLE subjects RENAME COLUMN year_new TO year;

-- Recreate the unique constraint with INTEGER year
ALTER TABLE subjects ADD CONSTRAINT uq_subject_code_semester_year 
    UNIQUE (subject_code, semester_name, year);

-- Recreate index on year (if needed for queries)
CREATE INDEX IF NOT EXISTS idx_subjects_year ON subjects(year);


-- ============================================================================
-- STEP 2: assignments table
-- ============================================================================
-- Add temporary INTEGER column
ALTER TABLE assignments ADD COLUMN year_new INTEGER;

-- Backfill from VARCHAR to INTEGER
UPDATE assignments SET year_new = year::INTEGER;

-- Make NOT NULL after backfill
ALTER TABLE assignments ALTER COLUMN year_new SET NOT NULL;

-- Drop the unique constraint that references the old year column
ALTER TABLE assignments DROP CONSTRAINT IF EXISTS uq_assignment;

-- Drop the old VARCHAR column
ALTER TABLE assignments DROP COLUMN year;

-- Rename new column to original name
ALTER TABLE assignments RENAME COLUMN year_new TO year;

-- Recreate the unique constraint with INTEGER year
ALTER TABLE assignments ADD CONSTRAINT uq_assignment 
    UNIQUE (assessment, subject_code, semester_name, year);

-- Recreate index on year (if needed for queries)
CREATE INDEX IF NOT EXISTS idx_assignments_year ON assignments(year);


-- ============================================================================
-- STEP 3: examinations table (PRIMARY KEY includes year)
-- ============================================================================
-- Strategy: Since year is part of the PRIMARY KEY, we need to:
-- 1. Drop the PRIMARY KEY constraint
-- 2. Add year_new INTEGER column and backfill
-- 3. Drop old year column
-- 4. Rename year_new to year
-- 5. Recreate PRIMARY KEY with INTEGER year

-- Drop PRIMARY KEY constraint
ALTER TABLE examinations DROP CONSTRAINT IF EXISTS examinations_pkey;

-- Add temporary INTEGER column
ALTER TABLE examinations ADD COLUMN year_new INTEGER;

-- Backfill from VARCHAR to INTEGER
UPDATE examinations SET year_new = year::INTEGER;

-- Make NOT NULL after backfill
ALTER TABLE examinations ALTER COLUMN year_new SET NOT NULL;

-- Drop the old VARCHAR column
ALTER TABLE examinations DROP COLUMN year;

-- Rename new column to original name
ALTER TABLE examinations RENAME COLUMN year_new TO year;

-- Recreate PRIMARY KEY with INTEGER year
ALTER TABLE examinations ADD CONSTRAINT examinations_pkey 
    PRIMARY KEY (subject_code, semester_name, year);

-- Recreate index on year (if needed for queries)
CREATE INDEX IF NOT EXISTS idx_examinations_year ON examinations(year);


-- ============================================================================
-- STEP 4: exam_settings table (PRIMARY KEY includes year)
-- ============================================================================
-- Same strategy as examinations

-- Drop PRIMARY KEY constraint
ALTER TABLE exam_settings DROP CONSTRAINT IF EXISTS exam_settings_pkey;

-- Add temporary INTEGER column
ALTER TABLE exam_settings ADD COLUMN year_new INTEGER;

-- Backfill from VARCHAR to INTEGER
UPDATE exam_settings SET year_new = year::INTEGER;

-- Make NOT NULL after backfill
ALTER TABLE exam_settings ALTER COLUMN year_new SET NOT NULL;

-- Drop the old VARCHAR column
ALTER TABLE exam_settings DROP COLUMN year;

-- Rename new column to original name
ALTER TABLE exam_settings RENAME COLUMN year_new TO year;

-- Recreate PRIMARY KEY with INTEGER year
ALTER TABLE exam_settings ADD CONSTRAINT exam_settings_pkey 
    PRIMARY KEY (subject_code, semester_name, year);

-- Recreate index on year (if needed for queries)
CREATE INDEX IF NOT EXISTS idx_exam_settings_year ON exam_settings(year);


-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- Check year column types:
-- SELECT table_name, column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_schema = 'public' AND column_name = 'year'
-- ORDER BY table_name;
--
-- Expected: All should show INTEGER (not character varying)

COMMIT;
