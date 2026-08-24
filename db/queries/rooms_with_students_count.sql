-- List of rooms and the number of students in each of them
SELECT r.id, r.name, COUNT(s.id) AS students_count
FROM rooms r
LEFT JOIN students s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY r.id;
