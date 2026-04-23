# Now you write the functions that actually read and write to SQLite. These are plain Python functions — no FastAPI here yet.
from backend.database import conn, cursor

def save_message(role: str, content: str):
    """
    Save one message (either 'user' or 'assistant') to the messages table
    """
    cursor.execute(
        "INSERT INTO messages (role, content) VALUES (?,?)", (role, content)
    )
    conn.commit()

def get_all_messages():
    """
    Fetch every message from the database, oldest first.
    Returns a list of dicts:
    [{"role": "user", "content": "Hello"}, ...]
    """
    cursor.execute(
        "SELECT role, content FROM messages ORDER BY id ASC"
    )
    rows = cursor.fetchall()

    # Convert list of tuples → list of dicts
    # row[0] = role, row[1] = content
    return [{"role": row[0], "content": row[1]} for row in rows]

# Routes will call these functions. Only this file shall change when I switch to PostgreSQL from SQLite
