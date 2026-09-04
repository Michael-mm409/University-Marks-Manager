-- Migration: Change Course.grading_scale from string to integer foreign key (grading_scale_id)
-- 1. Add new column grading_scale_id (nullable for now)
ALTER TABLE courses ADD COLUMN grading_scale_id INTEGER;

-- 2. If you want to migrate existing data, set grading_scale_id for all courses to the id of the 'Standard' scale (or another default)
-- Example: update all to the first grade scale (adjust as needed)
UPDATE courses SET grading_scale_id = (SELECT id FROM grade_scales WHERE scale_name = 'Standard' LIMIT 1);

-- 3. Set NOT NULL and add foreign key constraint
ALTER TABLE courses ALTER COLUMN grading_scale_id SET NOT NULL;
ALTER TABLE courses ADD CONSTRAINT fk_courses_grading_scale FOREIGN KEY (grading_scale_id) REFERENCES grade_scales(id);

-- 4. Drop the old grading_scale column
ALTER TABLE courses DROP COLUMN grading_scale;
