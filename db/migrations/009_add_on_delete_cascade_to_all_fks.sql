-- Migration 009: Add ON DELETE CASCADE to all foreign key constraints
-- 
-- This ensures that deleting a parent entity automatically removes all dependent records:
-- - Deleting a Course removes its Semesters (and transitively Subjects, Assignments, Exams)
-- - Deleting a Semester removes its Subjects (and transitively Assignments, Exams)
-- - Deleting a Subject removes its Assignments, Examinations, and ExamSettings
--
-- Current state: All FKs have delete_rule = 'NO ACTION'
-- Target state: All FKs have ON DELETE CASCADE

-- 1. semesters.course_id → courses.id
ALTER TABLE semesters 
    DROP CONSTRAINT IF EXISTS semesters_course_id_fkey;

ALTER TABLE semesters 
    ADD CONSTRAINT semesters_course_id_fkey 
    FOREIGN KEY (course_id) REFERENCES courses(id) 
    ON DELETE CASCADE;

-- 2. subjects.semester_id → semesters.id
ALTER TABLE subjects 
    DROP CONSTRAINT IF EXISTS subjects_semester_id_fkey;

ALTER TABLE subjects 
    ADD CONSTRAINT subjects_semester_id_fkey 
    FOREIGN KEY (semester_id) REFERENCES semesters(id) 
    ON DELETE CASCADE;

-- 3. assignments.subject_id → subjects.id
ALTER TABLE assignments 
    DROP CONSTRAINT IF EXISTS assignments_subject_id_fkey;

ALTER TABLE assignments 
    ADD CONSTRAINT assignments_subject_id_fkey 
    FOREIGN KEY (subject_id) REFERENCES subjects(id) 
    ON DELETE CASCADE;

-- 4. examinations.subject_id → subjects.id
ALTER TABLE examinations 
    DROP CONSTRAINT IF EXISTS examinations_subject_id_fkey;

ALTER TABLE examinations 
    ADD CONSTRAINT examinations_subject_id_fkey 
    FOREIGN KEY (subject_id) REFERENCES subjects(id) 
    ON DELETE CASCADE;

-- 5. exam_settings.subject_id → subjects.id
ALTER TABLE exam_settings 
    DROP CONSTRAINT IF EXISTS exam_settings_subject_id_fkey;

ALTER TABLE exam_settings 
    ADD CONSTRAINT exam_settings_subject_id_fkey 
    FOREIGN KEY (subject_id) REFERENCES subjects(id) 
    ON DELETE CASCADE;
