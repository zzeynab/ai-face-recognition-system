import pickle
import sqlite3
from datetime import datetime

from database.database import DB_PATH, initialize_database


class DatabaseService:
    """The only layer allowed to execute SQLite queries."""

    def __init__(self):
        self.db_path = DB_PATH
        initialize_database()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _capture_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------- People ----------

    def add_person(self, first_name, last_name, register_time):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO people (first_name, last_name, register_time)
                VALUES (?, ?, ?)
                """,
                (first_name, last_name, register_time),
            )
            return cursor.lastrowid

    def create_person_with_embeddings(
        self,
        first_name,
        last_name,
        register_time,
        pose_embeddings,
    ):
        """Create one person and all five samples in a single transaction."""
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO people (first_name, last_name, register_time)
                VALUES (?, ?, ?)
                """,
                (first_name, last_name, register_time),
            )
            person_id = cursor.lastrowid
            self._insert_embeddings(connection, person_id, pose_embeddings)
            return person_id

    def get_person(self, person_id):
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT id, first_name, last_name, register_time
                FROM people
                WHERE id = ?
                """,
                (person_id,),
            ).fetchone()

    def get_all_people(self):
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT id, first_name, last_name, register_time
                FROM people
                ORDER BY id DESC
                """
            ).fetchall()

    def search_people(self, text):
        search_text = f"%{text.strip()}%"
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT id, first_name, last_name, register_time
                FROM people
                WHERE first_name LIKE ? OR last_name LIKE ?
                ORDER BY id DESC
                """,
                (search_text, search_text),
            ).fetchall()

    def update_person(self, person_id, first_name, last_name):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE people
                SET first_name = ?, last_name = ?
                WHERE id = ?
                """,
                (first_name, last_name, person_id),
            )
            return cursor.rowcount > 0

    def delete_person(self, person_id):
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM people WHERE id = ?",
                (person_id,),
            )
            return cursor.rowcount > 0

    # ---------- Embeddings ----------

    def _insert_embeddings(self, connection, person_id, pose_embeddings):
        captured_at = self._capture_time()
        connection.executemany(
            """
            INSERT INTO embeddings (person_id, pose, embedding, captured_at)
            VALUES (?, ?, ?, ?)
            """,
            [
                (person_id, pose, pickle.dumps(embedding), captured_at)
                for pose, embedding in pose_embeddings.items()
            ],
        )

    def add_embedding(self, person_id, embedding, pose="front"):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO embeddings (person_id, pose, embedding, captured_at)
                VALUES (?, ?, ?, ?)
                """,
                (person_id, pose, pickle.dumps(embedding), self._capture_time()),
            )
            return cursor.lastrowid

    def add_embeddings(self, person_id, pose_embeddings):
        """Add five fresh pose samples to an existing person atomically."""
        if not pose_embeddings:
            return

        with self.connect() as connection:
            self._insert_embeddings(connection, person_id, pose_embeddings)

    def get_all_embeddings(self):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    people.id,
                    people.first_name,
                    people.last_name,
                    embeddings.id,
                    embeddings.pose,
                    embeddings.embedding
                FROM embeddings
                INNER JOIN people ON people.id = embeddings.person_id
                ORDER BY people.id, embeddings.id
                """
            ).fetchall()

        return [
            {
                "person_id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "embedding_id": row[3],
                "pose": row[4],
                "embedding": pickle.loads(row[5]),
            }
            for row in rows
        ]

    def get_embeddings_by_person(self, person_id):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, pose, embedding, captured_at
                FROM embeddings
                WHERE person_id = ?
                ORDER BY id
                """,
                (person_id,),
            ).fetchall()

        return [
            {
                "embedding_id": row[0],
                "pose": row[1],
                "embedding": pickle.loads(row[2]),
                "captured_at": row[3],
            }
            for row in rows
        ]

    def delete_embedding(self, embedding_id):
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM embeddings WHERE id = ?",
                (embedding_id,),
            )
            return cursor.rowcount > 0
