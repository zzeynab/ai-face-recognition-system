"""SQLite schema initialization and small forward-only migrations."""

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "faces.db"


def initialize_database():
    """Create the database schema without deleting existing registrations."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                register_time TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                pose TEXT NOT NULL DEFAULT 'front',
                embedding BLOB NOT NULL,
                captured_at TEXT,
                FOREIGN KEY (person_id)
                    REFERENCES people(id)
                    ON DELETE CASCADE
            )
            """
        )

        _add_column_if_missing(connection, "embeddings", "captured_at", "TEXT")

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_embeddings_person_id
            ON embeddings(person_id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_embeddings_pose
            ON embeddings(pose)
            """
        )


def _add_column_if_missing(connection, table_name, column_name, column_type):
    columns = {
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})")
    }

    if column_name not in columns:
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        )
