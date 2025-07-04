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
