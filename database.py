def add_coins(user_id: int, amount: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (user_id, coins) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET coins = coins + ?",
        (user_id, amount, amount)
    )
    conn.commit()
    conn.close()

def remove_coins(user_id: int, amount: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # On vérifie d'abord que l'utilisateur a assez de coins
    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    if not result or result[0] < amount:
        conn.close()
        return False  # Pas assez de coins
    cur.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
    return True

import sqlite3

DB_PATH = "boostcoins.db"

def get_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def get_top_users(limit: int = 3) -> list[tuple[int, int]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, coins FROM users ORDER BY coins DESC LIMIT ?", (limit,))
    results = cur.fetchall()
    conn.close()
    return results

def get_inventory(user_id: int) -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT item_name FROM inventory WHERE user_id = ?", (user_id,))
    results = cur.fetchall()
    conn.close()
    return [row[0] for row in results]

def get_shop_items() -> list[tuple[str, str, int]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, description, price FROM shop")
    results = cur.fetchall()
    conn.close()
    return results
