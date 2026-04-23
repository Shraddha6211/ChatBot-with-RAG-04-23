from fastapi import APIRouter
from backend.models import HistoryResponse, HistoryMessage
from backend.services.db_service import get_all_messages

router = APIRouter()

@router.get("/history", response_model=HistoryResponse)
def get_history():
    """
    GET /history
    
    No request body needed — this just returns everything.
    
    Response:
    {
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    }
    """
    raw_history = get_all_messages()

      # Convert each dict into a HistoryMessage Pydantic object
    # FastAPI uses this to validate the output shape
    messages = [
        HistoryMessage(role=m["role"], content=m["content"])
        for m in raw_history
    ]

    return HistoryResponse(history=messages)