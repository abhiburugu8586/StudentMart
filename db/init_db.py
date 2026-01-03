import sqlite3
from werkzeug.security import generate_password_hash

# Creates db/database.db from db/schema.sql and inserts initial data
connection = sqlite3.connect("database.db")

with open("schema.sql", "r", encoding="utf-8") as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Users (passwords are hashed, like workshop) :contentReference[oaicite:12]{index=12}
cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("password")))
cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            ("user1", generate_password_hash("password")))

# Categories
cur.execute("INSERT INTO categories (name) VALUES (?)", ("Groceries",))
cur.execute("INSERT INTO categories (name) VALUES (?)", ("Kitchen Items",))

# Sample products (owned by user1 -> id=2)
sample_products = [
    (2, 1, "Basmati Rice 5kg", "Long grain rice for daily cooking", 14.99,
     "https://m.media-amazon.com/images/I/61PlyCPcI3L._AC_SY300_SX300_QL70_ML2_.jpg", 30),
    (2, 1, "Toor Dal 1kg", "Protein-rich lentils", 3.49,
     "https://images.unsplash.com/photo-1604908177110-8a9c1d3c9c7b", 50),
    (2, 2, "Non-stick Frying Pan", "28cm pan for easy cooking", 12.99,
     "https://images.unsplash.com/photo-1588168333986-5078d3ae3976", 15),
]

cur.executemany("""
    INSERT INTO products (user, category, name, description, price, image_url, stock)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", sample_products)

connection.commit()
connection.close()

print("Database created: db/database.db")
