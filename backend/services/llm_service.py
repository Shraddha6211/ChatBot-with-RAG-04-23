# This function has one job: take a list of messages, call OpenAI, return the reply string.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Create the OpenAI client once (reused for every call)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm_reply(messages: list[dict]) -> str:
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
     # Always prepend a system message to give the bot its personality
    system_message = {
        "role": "system",
        "content": "You are a helpful and friendly assistant. Keep answers clear and concise."
    }

    # Build the full message list: system instruction + conversation history
    full_messages = [system_message] + messages

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=full_messages,
        max_tokens=500
    )

    # Extract just the reply text from the response object
    return response.choices[0].message.content