import argparse
import json
import os
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

import psycopg2
from dotenv import load_dotenv


class DatabaseClient:
    def __init__(self) -> None:
        load_dotenv()
        self._connection_kwargs = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "dbname": os.getenv("DB_NAME", "innowise_db"),
            "user": os.getenv("DB_USER", "me"),
            "password": os.getenv("DB_PASSWORD", "me"),
        }

    def connect(self):
        return psycopg2.connect(**self._connection_kwargs)


class DataLoader:
    def __init__(self, db: DatabaseClient) -> None:
        self._db = db

    def load(self, students_path: Path, rooms_path: Path) -> None:
        students = json.loads(students_path.read_text(encoding="utf-8"))
        rooms = json.loads(rooms_path.read_text(encoding="utf-8"))

        room_rows = [(room["id"], room["name"]) for room in rooms]
        student_rows = [
            (student["id"], student["name"], student["room"], student["birthday"], student["sex"])
            for student in students
        ]

        with self._db.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM students;")
                cursor.execute("DELETE FROM rooms;")
                cursor.executemany(
                    """
                    INSERT INTO rooms (id, name)
                    VALUES (%s, %s)
                    """,
                    room_rows,
                )
                cursor.executemany(
                    """
                    INSERT INTO students (id, name, room_id, birthday, sex)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    student_rows,
                )


class IndexManager:
    def __init__(self, db: DatabaseClient, index_sql_path: Path) -> None:
        self._db = db
        self._index_sql_path = index_sql_path

    def apply(self) -> None:
        index_sql = self._index_sql_path.read_text(encoding="utf-8")
        with self._db.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(index_sql)


class ReportRepository:
    def __init__(self, db: DatabaseClient, queries: dict[str, Path]) -> None:
        self._db = db
        self._queries = queries

    @staticmethod
    def _rows_from_cursor(cursor) -> list[dict[str, Any]]:
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

    def fetch_all_reports(self) -> dict[str, list[dict[str, Any]]]:
        reports: dict[str, list[dict[str, Any]]] = {}
        with self._db.connect() as connection:
            with connection.cursor() as cursor:
                for report_name, query_path in self._queries.items():
                    query_sql = query_path.read_text(encoding="utf-8")
                    cursor.execute(query_sql)
                    reports[report_name] = self._rows_from_cursor(cursor)
        return reports


class ReportFormatter:
    @staticmethod
    def to_json(reports: dict[str, list[dict[str, Any]]]) -> str:
        return json.dumps(reports, ensure_ascii=False, indent=2, default=str)

    @staticmethod
    def to_xml(reports: dict[str, list[dict[str, Any]]]) -> str:
        root = Element("reports")
        for report_name, rows in reports.items():
            report_node = SubElement(root, report_name)
            for row in rows:
                item = SubElement(report_node, "item")
                for key, value in row.items():
                    field = SubElement(item, key)
                    field.text = "" if value is None else str(value)
        return tostring(root, encoding="unicode")


class ReportService:
    def __init__(self, repository: ReportRepository, formatter: ReportFormatter) -> None:
        self._repository = repository
        self._formatter = formatter

    def generate(self, output_format: str) -> str:
        reports = self._repository.fetch_all_reports()
        if output_format == "xml":
            return self._formatter.to_xml(reports)
        return self._formatter.to_json(reports)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", required=True, help="Path to students JSON file")
    parser.add_argument("--rooms", required=True, help="Path to rooms JSON file")
    parser.add_argument("--format", choices=["json", "xml"], required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    queries = {
        "rooms_with_students_count": repo_root / "db/queries/rooms_with_students_count.sql",
        "top5_rooms_smallest_avg_age": repo_root / "db/queries/top5_rooms_smallest_avg_age.sql",
        "top5_rooms_largest_age_diff": repo_root / "db/queries/top5_rooms_largest_age_diff.sql",
        "rooms_with_mixed_sex": repo_root / "db/queries/rooms_with_mixed_sex.sql",
    }

    db = DatabaseClient()

    data_loader = DataLoader(db)
    data_loader.load(students_path=Path(args.students), rooms_path=Path(args.rooms))

    index_manager = IndexManager(db, index_sql_path=repo_root / "db" / "indexes.sql")
    index_manager.apply()

    report_service = ReportService(
        repository=ReportRepository(
            db=db,
            queries=queries,
        ),
        formatter=ReportFormatter(),
    )
    print(report_service.generate(args.format))


if __name__ == "__main__":
    main()
