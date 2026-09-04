-- 015_update_examination_unique_constraint.sql
-- Drop the old unique index on subject_id
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'ix_examinations_subject_id'
    ) THEN
        EXECUTE 'DROP INDEX IF EXISTS ix_examinations_subject_id';
    END IF;
END$$;

-- Update any legacy rows with NULL exam_type to 'main'
UPDATE examinations SET exam_type = 'main' WHERE exam_type IS NULL;

-- Add a new unique constraint on (subject_id, exam_type)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_examinations_subject_id_exam_type'
    ) THEN
        ALTER TABLE examinations ADD CONSTRAINT uq_examinations_subject_id_exam_type UNIQUE (subject_id, exam_type);
    END IF;
END$$;
