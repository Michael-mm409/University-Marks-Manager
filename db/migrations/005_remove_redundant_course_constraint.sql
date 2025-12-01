-- Migration: Remove redundant unique constraint on Course(name, code)
-- 
-- RATIONALE:
-- The Course table currently has two unique constraints:
-- 1. uq_course_code on (code) - ensures course codes are globally unique
-- 2. uq_course_name_code on (name, code) - ensures (name, code) pairs are unique
--
-- Since constraint #1 already ensures code is unique globally, constraint #2 is redundant.
-- If code is unique, then (name, code) will automatically be unique regardless of name.
-- Removing this redundant constraint simplifies the schema and reduces index overhead.
--
-- IMPACT:
-- - Removes one unique constraint and its underlying index
-- - No data loss or modification
-- - Application behavior unchanged (uniqueness still enforced via uq_course_code)

BEGIN;

-- ============================================================================
-- PRE-CHECK: Verify current constraints exist
-- ============================================================================
-- Uncomment to verify constraints before dropping:
-- SELECT constraint_name, constraint_type 
-- FROM information_schema.table_constraints 
-- WHERE table_name = 'courses' AND constraint_type = 'UNIQUE'
-- ORDER BY constraint_name;
--
-- Expected output should include both:
-- - uq_course_code
-- - uq_course_name_code


-- ============================================================================
-- Drop redundant unique constraint
-- ============================================================================
ALTER TABLE courses DROP CONSTRAINT IF EXISTS uq_course_name_code;


-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================
-- Verify only uq_course_code remains:
-- SELECT constraint_name, constraint_type 
-- FROM information_schema.table_constraints 
-- WHERE table_name = 'courses' AND constraint_type = 'UNIQUE'
-- ORDER BY constraint_name;
--
-- Expected: Only uq_course_code should be listed

COMMIT;
