import os
import sqlite3

DB_PATH = "boostcoins.db"

def init_db():
    full_path = os.path.abspath(DB_PATH)
    print(f"Initialisation DB à : {full_path}")  # Ajout print

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
    print("Tables créées ou déjà existantes.")
# Optionnel : créer la base et tables au lancement du module
if __name__ == "__main__":
    init_db()
