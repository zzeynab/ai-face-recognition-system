"""SQLite schema initialization and small forward-only migrations."""

import sqlite3
import sys
from pathlib import Path


def get_database_path():
    """
    در حالت اجرای عادی:
        database/faces.db

    در حالت فایل exe:
        کنار فایل exe
    """

    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent

    return base_dir / "faces.db"


DB_PATH = get_database_path()


def initialize_database():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

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

        _add_column_if_missing(
            connection,
            "embeddings",
            "captured_at",
            "TEXT",
        )

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
        for row in connection.execute(
            f"PRAGMA table_info({table_name})"
        )
    }

    if column_name not in columns:

        connection.execute(
            f"ALTER TABLE {table_name} "
            f"ADD COLUMN {column_name} {column_type}"
        )