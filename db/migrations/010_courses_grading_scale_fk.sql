-- Migration: Change courses.grading_scale to integer and add FK to grade_scales(id)
-- 1. Add new integer column
aLTER TABLE courses ADD COLUMN grading_scale_id integer;
-- 2. Populate new column from old (if possible, using scale_name)
UPDATE courses SET grading_scale_id = gs.id FROM grade_scales gs WHERE courses.grading_scale = gs.scale_name;
-- 3. Set NOT NULL if all rows are filled (optional, otherwise leave nullable for now)
-- ALTER TABLE courses ALTER COLUMN grading_scale_id SET NOT NULL;
-- 4. Add foreign key constraint
ALTER TABLE courses ADD CONSTRAINT fk_courses_grading_scale FOREIGN KEY (grading_scale_id) REFERENCES grade_scales(id);
-- 5. Drop old column
aLTER TABLE courses DROP COLUMN grading_scale;
-- 6. Optionally, rename new column to grading_scale
ALTER TABLE courses RENAME COLUMN grading_scale_id TO grading_scale;
