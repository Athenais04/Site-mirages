import sqlite3
import os

# -------------------- CHEMIN VERS LA DB --------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "boostcoins.db")

# -------------------- INITIALISATION --------------------
def init_db():
    full_path = os.path.abspath(DB_PATH)
    print(f"Initialisation DB à : {full_path}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER NOT NULL DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shop (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        price INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("Tables créées ou déjà existantes.")

if os.path.exists(DB_PATH):
    print(f"Fichier {DB_PATH} prêt.")
else:
    print(f"⚠️ Attention : {DB_PATH} non trouvé.")

# -------------------- USERS (Coins) --------------------
def add_coins(user_id: int, amount: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users(user_id, coins) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET coins = coins + ?
    """, (user_id, amount, amount))
    conn.commit()
    conn.close()

def remove_coins(user_id: int, amount: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def get_top_users(limit=3):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, coins FROM users ORDER BY coins DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------- INVENTORY --------------------
def add_item_to_inventory(user_id: int, item_name: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO inventory (user_id, item_name) VALUES (?, ?)", (user_id, item_name))
    conn.commit()
    conn.close()

def get_inventory(user_id: int) -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT item_name FROM inventory WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

# -------------------- SHOP --------------------
def add_shop_item(name: str, description: str, price: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO shop (name, description, price) VALUES (?, ?, ?)", (name, description, price))
    conn.commit()
    conn.close()

def get_shop_items() -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, description, price FROM shop")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_shop_item(name: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, description, price FROM shop WHERE name = ?", (name,))
    item = cur.fetchone()
    conn.close()
    return item

def update_shop_item(name: str, new_description: str, new_price: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE shop
        SET description = ?, price = ?
        WHERE name = ?
    """, (new_description, new_price, name))
    conn.commit()
    conn.close()

def delete_shop_item(name: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM shop WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def buy_item(user_id: int, item_name: str) -> bool:
    item = get_shop_item(item_name)
    if not item:
        return False  # L'objet n'existe pas

    name, desc, price = item
    balance = get_balance(user_id)

    if balance < price:
        return False  # Pas assez de coins

    remove_coins(user_id, price)
    add_item_to_inventory(user_id, item_name)
    return True

