"""
Before writing any endpoint, you define what JSON goes in and what JSON comes out. These are called Pydantic models — FastAPI uses them to automatically validate requests.
"""

from pydantic import BaseModel

# Request models ( what the client sends to the api)

class ChatRequest(BaseModel):
    """
    Shape of JSON body for POST/ chat

    Example incoming JSON:
    {
        "message":"What is Python?"
    }
    """
    message: str

# Response models (what the api sends back to the client)

class ChatResponse(BaseModel):
    """
    Example outgoing JSON:
    {
        "reply": "Python is a progr..."
    }
    """
    reply: str


class HistoryMessage(BaseModel):
    """A single message in the history list"""
    role: str       # "user" or "assistant"
    content: str

class HistoryResponse(BaseModel):
    """
    Example outgoing JSON:
    {
        "history":[
            {"role": "user", "content", "Hello"},
            {"role": "assistant", "content", "Hi there!"}
        ]
    }
    """
    history: list[HistoryMessage]

### New: Upload models

class UploadResponse(BaseModel):
    """
    Returned after a document is uploaded and processed.

    Example response:
    {
        "success": true,
        "filename": "company_policy.pdf",
        "chunks_stored": 14
    }

    chunks_stored tells you how many pieces the document was split into.
    Useful for debugging -if you upload a 50-page PDF and get 2 chunks, somenthing went wrong with parsing.
    """
    success: bool
    filename: str
    chunks_stored: int