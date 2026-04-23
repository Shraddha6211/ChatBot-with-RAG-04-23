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