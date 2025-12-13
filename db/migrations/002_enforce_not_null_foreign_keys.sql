-- Migration 002: Enforce NOT NULL on new foreign key columns once backfilled.
-- Pre-check each column for NULLs; if any exist, backfill or delete rows before altering.
-- Example backfill strategy (if you can derive semester_id / subject_id from existing natural keys):
-- UPDATE subjects s SET semester_id = sem.id
-- FROM semesters sem
-- WHERE s.semester_id IS NULL AND sem.name = s.semester_name AND sem.year::text = s.year;
-- (Adjust CASTs as needed if year types differ.)

-- Verify no NULLs remain:
-- SELECT COUNT(*) FROM subjects WHERE semester_id IS NULL;
-- SELECT COUNT(*) FROM assignments WHERE subject_id IS NULL;
-- SELECT COUNT(*) FROM examinations WHERE subject_id IS NULL;
-- SELECT COUNT(*) FROM exam_settings WHERE subject_id IS NULL;

ALTER TABLE subjects ALTER COLUMN semester_id SET NOT NULL;
ALTER TABLE assignments ALTER COLUMN subject_id SET NOT NULL;
ALTER TABLE examinations ALTER COLUMN subject_id SET NOT NULL;
ALTER TABLE exam_settings ALTER COLUMN subject_id SET NOT NULL;
