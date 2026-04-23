from fastapi import APIRouter
from backend.models import ChatRequest, ChatResponse
from backend.services.db_service import save_message, get_all_messages
from backend.services.llm_service import get_llm_reply

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(data:ChatRequest):
    """
    POST /chat
    
    The core flow:
    1. Save the user's message to DB
    2. Load full history from DB
    3. Send history to LLM
    4. Save bot's reply to DB
    5. Return the reply
    
    Request body:
    {
        "message": "What is Python?"
    }
    
    Response:
    {
        "reply": "Python is a high-level programming language..."
    }
    """

    # Step 1: Save what the user just said
    save_message("user", data.message)

    # Step 2: Load the full conversation (including the message we just saved)
    history = get_all_messages()

    # Step 3: Get the LLM's reply
    bot_reply = get_llm_reply(history)

    # Step 4: Save the bot's reply
    save_message("assistant", bot_reply)

    # Step 5: Send the reply back to whoever called this endpoint
    return ChatResponse(reply=bot_reply)