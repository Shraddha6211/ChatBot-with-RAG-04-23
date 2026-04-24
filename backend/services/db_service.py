# Now you write the functions that actually read and write to SQLite. These are plain Python functions — no FastAPI here yet.
from backend.database import conn, cursor
from backend.services.rag_service import deserialize_embedding

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

def save_document(filename: str) -> int:
    """
    Insert a record for the uploaded file. Returns the new document's ID.
    This ID is used to link chunks back to their source document.
    """
    cursor.execute(
        "INSERT INTO documents (filename) VALUES (?)",
        (filename,)
    )
    conn.commit()
    return cursor.lastrowid # the auto-generated id for this document

def save_chunk(doc_id: int, content: str, embedding_str: str):
    """
    Save one chunk of text and its serialized embedding vector.

    doc_id:        which document this chunk came from
    content:       the raw text of this chunk
    embedding_str: the vector as a comma-separated string
    """
    cursor.execute(
        "INSERT INTO chunks (doc_id, content, embedding) VALUES (?, ?,?)", (doc_id, content, embedding_str)
    )
    conn.commit()


def get_all_chunks() -> list[dict]:
    """
    Load every chunk from the database, deserializing the embedding
    back from string → list of floats so we can do math on it.

    Returns:
    [
        {"content": "The refund policy states...", "embedding": [0.1, 0.2, ...]},
        ...
    ]
    """
    cursor.execute("SELECT content, embedding FROM chunks")
    rows = cursor.fetchall()

    return [
        {
            "content": row[0],
            "embedding": deserialize_embedding(row[1])     # string -> list[float]
        }
        for row in rows
    ]