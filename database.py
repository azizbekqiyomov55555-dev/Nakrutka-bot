import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product TEXT,
        amount INTEGER,
        status TEXT
    )
    """)
    conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def add_order(user_id, product, amount):
    cursor.execute("INSERT INTO orders (user_id, product, amount, status) VALUES (?, ?, ?, ?)",
                   (user_id, product, amount, "pending"))
    conn.commit()

def get_users():
    cursor.execute("SELECT user_id FROM users")
    return cursor.fetchall()

def get_orders():
    cursor.execute("SELECT * FROM orders")
    return cursor.fetchall()
