PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS task_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_slug TEXT NOT NULL UNIQUE,
    folder_path TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    checkpoint_name TEXT NOT NULL,
    score INTEGER,
    comment TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task_submissions(id) ON DELETE CASCADE
);

CREATE TRIGGER IF NOT EXISTS trg_task_submissions_updated_at
AFTER UPDATE ON task_submissions
FOR EACH ROW
BEGIN
    UPDATE task_submissions
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
