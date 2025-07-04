import sqlite3

DB_PATH = "boostcoins.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

def get_balance(user_id: int) -> int:
    conn = sqlite3.connect("boostcoins.db")
    cursor = conn.cursor()
    cursor.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return 0

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

    # Crée la table users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER NOT NULL DEFAULT 0
    )
    """)

    # Crée la table inventory
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    # Crée la table shop
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shop (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
