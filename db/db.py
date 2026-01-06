import os
import sqlite3
from flask import abort
from werkzeug.security import check_password_hash, generate_password_hash

__all__ = [
    "get_db_connection",
    "create_user",
    "validate_login",
    "get_user_by_username",
    "get_user_by_id",
    "get_all_categories",
    "get_all_products",
    "get_product_by_id",
    "create_product",
    "update_product",
    "delete_product","cart_add_item",
    "cart_get_items",
    "cart_update_quantity",
    "cart_clear",
    "order_create_from_cart",
    "order_get",
    "order_get_items",
    "orders_for_user",
    "search_products",
    "is_user_admin",

]

def get_db_connection():
    # DB is stored in db/database.db (absolute path to avoid OneDrive issues)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Auth ----------
def create_user(username, password):
    hashed = generate_password_hash(password)
    conn = get_db_connection()
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

def validate_login(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password"], password):
        return user
    return None

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user

# Catalog 
def get_all_categories():
    conn = get_db_connection()
    cats = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
    conn.close()
    return cats

def get_all_products(category_id=None, limit=None, order_by="created DESC"):
    conn = get_db_connection()
    query = """
        SELECT products.*, categories.name AS category_name
        FROM products
        JOIN categories ON products.category = categories.id
    """
    params = []
    if category_id:
        query += " WHERE categories.id = ?"
        params.append(category_id)

    query += f" ORDER BY {order_by}"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    rows = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    return rows

def search_products(keyword, limit=12):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT products.*, categories.name AS category_name
        FROM products
        JOIN categories ON products.category = categories.id
        WHERE products.name LIKE ?
        ORDER BY created DESC
        LIMIT ?
        """,
        (f"%{keyword}%", limit)
    ).fetchall()
    conn.close()
    return rows

def get_product_by_id(product_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT products.*, categories.name AS category_name
        FROM products
        JOIN categories ON products.category = categories.id
        WHERE products.id = ?
    """, (product_id,)).fetchone()
    conn.close()
    return row

# Product CRUD  
def create_product(user_id, category_id, name, description, price, image_url, stock):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO products (user, category, name, description, price, image_url, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, category_id, name, description, price, image_url, stock))
    conn.commit()
    conn.close()

def update_product(product_id, category_id, name, description, price, image_url, stock):
    conn = get_db_connection()
    conn.execute("""
        UPDATE products
        SET category=?, name=?, description=?, price=?, image_url=?, stock=?
        WHERE id=?
    """, (category_id, name, description, price, image_url, stock, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

# Cart helpers

def cart_add_item(user_id, product_id, qty=1):
    conn = get_db_connection()

    # Insert new row, or if exists, increase quantity
    conn.execute("""
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, product_id)
        DO UPDATE SET quantity = quantity + excluded.quantity
    """, (user_id, product_id, qty))

    conn.commit()
    conn.close()

def cart_get_items(user_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT cart_items.product_id, cart_items.quantity,
               products.name, products.price, products.image_url
        FROM cart_items
        JOIN products ON cart_items.product_id = products.id
        WHERE cart_items.user_id = ?
        ORDER BY products.name ASC
    """, (user_id,)).fetchall()
    conn.close()
    return rows

def cart_update_quantity(user_id, product_id, qty):
    conn = get_db_connection()
    if qty <= 0:
        conn.execute("DELETE FROM cart_items WHERE user_id=? AND product_id=?", (user_id, product_id))
    else:
        conn.execute("""
            UPDATE cart_items
            SET quantity=?
            WHERE user_id=? AND product_id=?
        """, (qty, user_id, product_id))
    conn.commit()
    conn.close()

def cart_clear(user_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM cart_items WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# Orders helpers

def order_create_from_cart(user_id):
    items = cart_get_items(user_id)
    if not items:
        return None  # nothing to checkout

    total = sum(row["price"] * row["quantity"] for row in items)

    conn = get_db_connection()
    cur = conn.cursor()

    # Create order
    cur.execute("""
        INSERT INTO orders (user_id, total, status)
        VALUES (?, ?, ?)
    """, (user_id, total, "placed"))
    order_id = cur.lastrowid

    # Add order lines
    for row in items:
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price_each)
            VALUES (?, ?, ?, ?)
        """, (order_id, row["product_id"], row["quantity"], row["price"]))

    conn.commit()
    conn.close()

    # Clear cart after successful order
    cart_clear(user_id)
    return order_id

def order_get(order_id):
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.close()
    return order

def order_get_items(order_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT order_items.quantity, order_items.price_each,
               products.name
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
    """, (order_id,)).fetchall()
    conn.close()
    return rows

def orders_for_user(user_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM orders
        WHERE user_id=?
        ORDER BY created DESC
    """, (user_id,)).fetchall()
    conn.close()
    return rows

def is_user_admin(user_id):
    conn = get_db_connection()
    row = conn.execute("SELECT is_admin FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return bool(row and row["is_admin"] == 1)


