from fastapi import APIRouter
from backend.models import ChatRequest, ChatResponse
from backend.services.db_service import (
    save_message, 
    get_all_messages,
    get_all_chunks
)
from backend.services.rag_service import (
    get_embedding,
    find_relevant_chunks
)
from backend.services.llm_service import get_llm_reply

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(data:ChatRequest):
    """
    # POST /chat
    
    # The core flow:
    # 1. Save the user's message to DB
    # 2. Load full history from DB
    # 3. Send history to LLM
    # 4. Save bot's reply to DB
    # 5. Return the reply
    
    # Request body:
    # {
    #     "message": "What is Python?"
    # }
    
    # Response:
    # {
    #     "reply": "Python is a high-level programming language..."
    # }

    POST /chat — now RAG-enhanced.

    New flow vs old flow:

    OLD: save message → load history → call LLM → save reply
    NEW: save message → load history → embed question
                     → retrieve relevant chunks → build context
                     → call LLM with context → save reply

    If no chunks exist in the DB (no documents uploaded yet),
    find_relevant_chunks returns [] and context becomes "",
    so get_llm_reply falls back to normal conversation mode.


    """

    # Step 1: Save what the user just said
    save_message("user", data.message)

    # Step 2: Load the full conversation (including the message we just saved)
    history = get_all_messages()

    # # Step 3: Get the LLM's reply
    # bot_reply = get_llm_reply(history)

    # # Step 4: Save the bot's reply
    # save_message("assistant", bot_reply)

    # # Step 5: Send the reply back to whoever called this endpoint
    # return ChatResponse(reply=bot_reply)

    all_chunks = get_all_chunks()

    context = ""    # default: no context

    if all_chunks:
        # Embed the user's question to get its vector
        question_embedding = get_embedding(data.message)

        # Find the 3 most relevant chunks from the database
        relevant_chunks = find_relevant_chunks(question_embedding, all_chunks, top_k=3)

        # Join the chunks into a single context string
        # Each chunk is separated by a clear divider so the LLM
        # can distinguish between different source passage
        context = "\n\n---\n\n".join(relevant_chunks)

    # Call LLM - passes context if we have it, empty string if not
    bot_reply = get_llm_reply(history, context=context)

    # Save bot reply (unchanged)
    save_message("assistant", bot_reply)

    return ChatResponse(reply=bot_reply)