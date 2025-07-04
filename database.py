import sqlite3

DB_PATH = "boostcoins.db"

def get_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def get_top_users(limit=3):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, coins FROM users ORDER BY coins DESC LIMIT ?", (limit,))
    result = cur.fetchall()
    conn.close()
    return result

def get_shop_items():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, description, price FROM shop_items")
    items = cur.fetchall()
    conn.close()
    return items
