import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "faces.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ===============================
# People Table
# ===============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS people(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    register_time TEXT NOT NULL
)
""")

# ===============================
# Embeddings Table
# ===============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS embeddings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    pose TEXT NOT NULL,
    embedding BLOB NOT NULL,

    FOREIGN KEY(person_id)
    REFERENCES people(id)
    ON DELETE CASCADE
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")