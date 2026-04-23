import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

def create_tables():
    """
    Create all tables when the app starts.
    IF NOT EXISTS means this is safe to call every time — it won't
    wipe your data if the table already exists.
    """

    # Table 1: Store every chat message (user + assistant turns)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            role      TEXT NOT NULL,
            content   TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

