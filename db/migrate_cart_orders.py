import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Cart items (doesn't delete old data)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id),
          product_id INTEGER NOT NULL REFERENCES products(id),
          quantity INTEGER NOT NULL DEFAULT 1,
          UNIQUE(user_id, product_id)
        );
    """)

    # Orders + order items (doesn't delete old data)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id),
          created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          status TEXT NOT NULL DEFAULT 'placed',
          total REAL NOT NULL DEFAULT 0
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          order_id INTEGER NOT NULL REFERENCES orders(id),
          product_id INTEGER NOT NULL REFERENCES products(id),
          quantity INTEGER NOT NULL DEFAULT 1,
          price_each REAL NOT NULL
        );
    """)

    conn.commit()
    conn.close()
    print("Migration complete: cart_items, orders, order_items added (old data kept).")

if __name__ == "__main__":
    migrate()
