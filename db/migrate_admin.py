import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Add is_admin column if it doesn't exist
    cur.execute("PRAGMA table_info(users);")
    cols = [row[1] for row in cur.fetchall()]
    if "is_admin" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0;")
        conn.commit()
        print("✅ Added is_admin column to users")
    else:
        print("ℹ️ is_admin already exists")

    conn.close()

if __name__ == "__main__":
    migrate()
