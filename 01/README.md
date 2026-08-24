# Task 01

Loads `students` and `rooms` into PostgreSQL, creates indexes, and exports 4 reports in JSON or XML.

## Run

```bash
uv run python 01/scripts/init_db.py
uv run python 01/scripts/reports.py --students 01/data/students.json --rooms 01/data/rooms.json --format json
uv run python 01/scripts/reports.py --students 01/data/students.json --rooms 01/data/rooms.json --format xml
```
