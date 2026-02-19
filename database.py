import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        referral INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product TEXT,
        price INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS promocodes (
        code TEXT PRIMARY KEY,
        amount INTEGER
    )
    """)

    conn.commit()


def add_user(user_id, referral=None):
    cursor.execute("INSERT OR IGNORE INTO users(user_id, referral) VALUES (?,?)",
                   (user_id, referral))
    conn.commit()


def add_product(name, price):
    cursor.execute("INSERT INTO products(name,price) VALUES (?,?)",
                   (name, price))
    conn.commit()


def get_products():
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


def add_order(user_id, product, price):
    cursor.execute("INSERT INTO orders(user_id,product,price) VALUES (?,?,?)",
                   (user_id, product, price))
    conn.commit()


def get_orders():
    cursor.execute("SELECT * FROM orders")
    return cursor.fetchall()


def get_users():
    cursor.execute("SELECT user_id FROM users")
    return cursor.fetchall()


def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",
                   (amount, user_id))
    conn.commit()


def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]


def add_promocode(code, amount):
    cursor.execute("INSERT OR REPLACE INTO promocodes(code,amount) VALUES (?,?)",
                   (code, amount))
    conn.commit()


def get_promocode(code):
    cursor.execute("SELECT amount FROM promocodes WHERE code=?", (code,))
    return cursor.fetchone()
