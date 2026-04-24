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

    # Table to keep track of each uploaded document(entire files)
    # Chunks are kept separately so that you can list files later, or delete a whole document, or show which doc a chunk came from 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table to store each chunk of text and its embedding vector
    # doc_id links back to documents table (which file this came from)
    # into a comma-separated string and deserialize when reading back

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id      INTEGER NOT NULL,
            content     TEXT NOT NULL,
            embedding   TEXT NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
                   )
""")

    conn.commit()

