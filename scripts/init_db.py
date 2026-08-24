import os
import sqlite3
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "db" / "schema.sql"
    db_path = Path(os.getenv("DB_PATH", "data/innowise_tasks.db"))
    absolute_db_path = db_path if db_path.is_absolute() else repo_root / db_path

    absolute_db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(absolute_db_path) as connection:
        schema_sql = schema_path.read_text(encoding="utf-8")
        connection.executescript(schema_sql)
        connection.commit()

    print(f"Database is ready: {absolute_db_path}")


if __name__ == "__main__":
    main()
