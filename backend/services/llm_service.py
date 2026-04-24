# This function has one job: take a list of messages, call OpenAI, return the reply string.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Create the OpenAI client once (reused for every call)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm_reply(messages: list[dict], context: str = "") -> str:
    """
    Send a conversation history to OpenAI and return the reply text.

    'messages' looks like:
    [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
        {"role": "user", "content": "What is Python?"}
    ]

    The model sees the full history and replies in context.
    """

     # Build system prompt based on whether we have context
    if context:
        # RAG mode: tell the LLM explicitly to use the provided context
        # and admit when it doesn't know rather than making things up
        system_content = f"""You are a helpful assistant that answers questions 
based on the provided document context.

CONTEXT FROM UPLOADED DOCUMENTS:
{context}

Instructions:
- Answer using the context above as your primary source
- If the answer is clearly in the context, use it directly
- If the context doesn't contain enough information, say so honestly
- Do not make up information that isn't in the context"""
    else:
        # Fallback mode: no documents uploaded yet, behave normally
        system_content = "You are a helpful and friendly assistant. Keep answers clear and concise."


     # Always prepend a system message to give the bot its personality
    system_message = {
        "role": "system",
        "content": system_content
    }

    # Build the full message list: system instruction + conversation history
    full_messages = [system_message] + messages

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=full_messages,
        max_tokens=700      # slightly more tokens now since context is larger
    )

    # Extract just the reply text from the response object
    return response.choices[0].message.content