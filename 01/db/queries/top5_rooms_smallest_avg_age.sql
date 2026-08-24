-- 5 rooms with the smallest average age of students
SELECT
    r.id,
    r.name,
    ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))),2) AS avg_age
FROM rooms r
JOIN students s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY avg_age ASC
LIMIT 5;
