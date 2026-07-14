import sqlite3

conn = sqlite3.connect("database/faces.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS faces(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    register_time TEXT,
    embedding BLOB
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")