-- Migration: Add university table and university_id to courses

-- 1. Create university table
CREATE TABLE IF NOT EXISTS university (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- 2. Add university_id column to courses
ALTER TABLE courses ADD COLUMN IF NOT EXISTS university_id INTEGER;

-- 3. Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_courses_university'
          AND table_name = 'courses'
    ) THEN
        ALTER TABLE courses ADD CONSTRAINT fk_courses_university FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE SET NULL;
    END IF;
END$$;