from pathlib import Path


def test_schema_contains_main_tables() -> None:
    schema = Path("db/schema.sql").read_text(encoding="utf-8")
    assert "task_submissions" in schema
    assert "task_checkpoints" in schema
