import os
import pickle
import sqlite3


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "faces.db")


class DatabaseService:

    def __init__(self):
        self.db_path = DB_PATH

    # ==========================================
    # Connection
    # ==========================================

    def connect(self):
        return sqlite3.connect(self.db_path)

    # ==========================================
    # People
    # ==========================================

    def add_person(
        self,
        first_name,
        last_name,
        register_time
    ):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO people(
                    first_name,
                    last_name,
                    register_time
                )
                VALUES (?, ?, ?)
                """,
                (
                    first_name,
                    last_name,
                    register_time
                )
            )

            return cursor.lastrowid

    def get_person(self, person_id):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    register_time
                FROM people
                WHERE id=?
                """,
                (person_id,)
            )

            return cursor.fetchone()

    def get_all_people(self):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    register_time
                FROM people
                ORDER BY id DESC
                """
            )

            return cursor.fetchall()

    def search_people(self, text):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    register_time
                FROM people
                WHERE first_name LIKE ?
                   OR last_name LIKE ?
                ORDER BY id DESC
                """,
                (
                    f"%{text}%",
                    f"%{text}%"
                )
            )

            return cursor.fetchall()

    def update_person(
        self,
        person_id,
        first_name,
        last_name
    ):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE people
                SET
                    first_name=?,
                    last_name=?
                WHERE id=?
                """,
                (
                    first_name,
                    last_name,
                    person_id
                )
            )

    def delete_person(self, person_id):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM embeddings
                WHERE person_id=?
                """,
                (person_id,)
            )

            cursor.execute(
                """
                DELETE FROM people
                WHERE id=?
                """,
                (person_id,)
            )

    # ==========================================
    # Embeddings
    # ==========================================

    def add_embedding(
        self,
        person_id,
        embedding,
        pose="front"
    ):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO embeddings(
                    person_id,
                    pose,
                    embedding
                )
                VALUES (?, ?, ?)
                """,
                (
                    person_id,
                    pose,
                    pickle.dumps(embedding)
                )
            )

    def get_all_embeddings(self):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    people.id,
                    people.first_name,
                    people.last_name,
                    embeddings.id,
                    embeddings.pose,
                    embeddings.embedding
                FROM embeddings
                INNER JOIN people
                    ON people.id = embeddings.person_id
                """
            )

            rows = cursor.fetchall()

        result = []

        for row in rows:

            result.append({

                "person_id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "embedding_id": row[3],
                "pose": row[4],
                "embedding": pickle.loads(row[5])

            })

        return result

    def get_embeddings_by_person(self, person_id):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    pose,
                    embedding
                FROM embeddings
                WHERE person_id=?
                """,
                (person_id,)
            )

            rows = cursor.fetchall()

        result = []

        for row in rows:

            result.append({

                "embedding_id": row[0],
                "pose": row[1],
                "embedding": pickle.loads(row[2])

            })

        return result

    def delete_embedding(self, embedding_id):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM embeddings
                WHERE id=?
                """,
                (embedding_id,)
            )