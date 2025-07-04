import sqlite3

DB_PATH = "boostcoins.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Création table users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER NOT NULL DEFAULT 0
    )
    """)

    # Création table inventory
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    # Création table shop
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

def get_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    if result:
        return result[0]
    return 0

def add_coins(user_id: int, amount: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Vérifie si l'utilisateur existe
    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()

    if result:
        # Met à jour le solde
        new_balance = result[0] + amount
        cur.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
    else:
        # Crée un nouvel utilisateur avec le montant
        cur.execute("INSERT INTO users (user_id, coins) VALUES (?, ?)", (user_id, amount))

    conn.commit()
    conn.close()

def remove_coins(user_id: int, amount: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()

    if result:
        new_balance = max(0, result[0] - amount)
        cur.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))

    conn.commit()
    conn.close()

# Optionnel : créer la base et tables au lancement du module
if __name__ == "__main__":
    init_db()
