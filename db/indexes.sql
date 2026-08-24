CREATE INDEX IF NOT EXISTS idx_students_room_id_birthday ON students(room_id, birthday);
-- b-tree композитный индекс по полям room_id и birthday таблицы students,
-- Работает по левому префиксу, и можно испльзовать для фильтрации/агрегации по room_id и room_id + birthday,
-- но не используется для фильтрации/агрегации только по birthday.
