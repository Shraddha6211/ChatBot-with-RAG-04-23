import os
import math
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# PHASE 1 HELPERS: Indexing

def split_into_chunks(text: str, chunk_size: int = 500) -> list[str]:
    """
    Split a long text into smaller overlapping chunks.

    Why chunk at all?? LLMs have a context window limit - you can't paste a 100 page document into a prompt. Chunking lets you find and inject only the RELEVANT parts.

    Why overlap? If a key sentence sits at the boundary between two chunks, overlap ensures it appears fully in at least one chunk. 

    chunk_size=500: roughly one paragraph. Tune this based on your docs. 
    overlap =100: last 100 words of chunk N become first 100 of chunk N+1

    Example with chunk_size=10, overlap=3, text="A B C D E F G H I J K L":
        Chunk 1: "A B C D E F G H I J"
        Chunk 2: "H I J K L"          ← starts 3 words before chunk 1 ended
    """

    words = text.split()
    overlap = 100
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        # Move forward by (chunk_size -overlap) so next chunk
        # starts overlap words before this one ended
        start += chunk_size - overlap

    return chunks

def get_embedding(text: str) -> list[float]:
    """
    Call OpenAI's embedding API and return a vector (list of floats).
    text-embedding-3-small returns 1536-dimensional vectors.
    "Dimensional" just means the list has 1536 numbers.

    This is a separate API from chat completions - it doesn't generate text, it converts text into its mathematical meaning-representation.

    Cost: much cheaper than chat completions. Embeddings are designed to be called thousands of times.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    # The vector lives here - a list of 1536 floats
    return response.data[0].embedding

def serialize_embedding(embedding: list[float]) -> str:
    """
    Convert a list of floats to a comma-separated string for SQLite storage. 

    [0.1, 0.2, 0.3] → "0.1,0.2,0.3"
    """
    return ",".join(str(x) for x in embedding)

def deserialize_embedding(embedding_str: str) -> list[float]:
    """
    Convert the stored string back to a list of floats for math operations.
    
    "0.1,0.2,0.3" → [0.1, 0.2, 0.3]
    """
    return [float(x) for x in embedding_str.split(",")]

### PHASE 2 HELPERS: Retrieval

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Measure how similar two vectors are. Return a score from 0 to 1.

    1.0 = identical meaning
    0.0 = completely unrelated

    The math:
        similarity = (A · B) / (|A| × |B|)

    A · B  = dot product = sum of (a_i × b_i) for all dimensions
    |A|    = magnitude = sqrt(sum of a_i²)

    Don't worry about memorizing this formula. Just understand:
    - High score = vectors point in same direction = similar meaning
    - Low score  = vectors point in different directions = different meaning
    """
    dot_product = sum(a * b for a, b in zip( vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    # Avoid division by zero if either vector is all zeros
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)

def find_relevant_chunks(
        question_embedding: list[float],
        all_chunks: list[dict],
        top_k: int = 3
) -> list[str]:
    """
    Given a question's embedding and all stored chunks,
    return the top_k most relevant chunk texts.

    all_chunks is a list of dicts:
    [{"content": "...", "embedding": [0.1, 0.2, ...]}, ...]

    Process:
    1. Score each chunk by cosine similarity to the question
    2. Sort by score descending
    3. Return the top_k chunk texts

    top_k=3 is a common default. More chunks = more context but also
    more tokens sent to the LLM (costs more, may dilute focus).
    """
    scored = []

    for chunk in all_chunks:
        score = cosine_similarity(question_embedding, chunk["embedding"])
        scored.append((score, chunk["content"]))

    # Sort by score, highest first
    scored.sort(key=lambda x: x[0], reverse=True)

    # Return only the text of the top_k results
    return [content for score, content in scored[:top_k]]