-- Calculate Weighted Average Mark (WAM) for a course
-- WAM = Sum(total_mark * credit_points) / Sum(credit_points)
-- Only includes subjects with total_mark > 0

-- Overall WAM for a specific course
SELECT 
    c.id as course_id,
    c.name as course_name,
    ROUND(
        SUM(s.total_mark * s.credit_points)::NUMERIC / 
        NULLIF(SUM(s.credit_points), 0),
        2
    ) as wam,
    SUM(s.credit_points) as total_credit_points,
    COUNT(s.id) as subject_count
FROM subjects s
INNER JOIN semesters sem ON s.semester_id = sem.id
INNER JOIN courses c ON sem.course_id = c.id
WHERE s.total_mark > 0
    AND s.total_mark IS NOT NULL
    AND c.id = 1 -- Replace 1 with your course_id
GROUP BY c.id, c.name;

-- Optional: WAM by semester within a course
SELECT 
    c.id as course_id,
    c.name as course_name,
    sem.id as semester_id,
    sem.name as semester_name,
    sem.year,
    ROUND(
        SUM(s.total_mark * s.credit_points)::NUMERIC / 
        NULLIF(SUM(s.credit_points), 0),
        2
    ) as semester_wam,
    SUM(s.credit_points) as semester_credit_points,
    COUNT(s.id) as subject_count
FROM subjects s
INNER JOIN semesters sem ON s.semester_id = sem.id
INNER JOIN courses c ON sem.course_id = c.id
WHERE s.total_mark > 0
    AND s.total_mark IS NOT NULL
    AND c.id = 1 -- Replace 1 with your course_id
GROUP BY c.id, c.name, sem.id, sem.name, sem.year
ORDER BY sem.year ASC, sem.name ASC;

-- Optional: Detailed breakdown by subject (for verification)
SELECT 
    s.id,
    s.subject_code,
    s.subject_name,
    sem.name as semester_name,
    sem.year,
    s.credit_points,
    s.total_mark,
    ROUND((s.total_mark * s.credit_points)::NUMERIC, 2) as weighted_contribution
FROM subjects s
INNER JOIN semesters sem ON s.semester_id = sem.id
INNER JOIN courses c ON sem.course_id = c.id
WHERE s.total_mark > 0
    AND s.total_mark IS NOT NULL
    AND c.id = 1 -- Replace 1 with your course_id
ORDER BY sem.year ASC, sem.name ASC, s.subject_code ASC;
