--5 rooms with the largest difference in the age of students
SELECT
    r.id,
    r.name,
    ROUND(MAX(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))) - MIN(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))),2) AS age_diff
FROM rooms r
JOIN students s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY age_diff DESC
LIMIT 5;
