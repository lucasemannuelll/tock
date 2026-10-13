import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "time_tracker.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    if not DB_PATH.exists():
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn = get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()


