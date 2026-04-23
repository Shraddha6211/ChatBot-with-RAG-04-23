# frontend/app.py

import streamlit as st
import requests

# The base URL of your running FastAPI backend
API_BASE = "http://127.0.0.1:8000"


# ── Main Area: Chat Interface ────────────────────────────────────────────────

st.title("🤖 My Chatbot")

# Load chat history from the backend on every page render
history_response = requests.get(f"{API_BASE}/history")
history = history_response.json().get("history", [])

# Render all past messages as chat bubbles
for msg in history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input at the bottom
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Send to backend — it handles DB saving + LLM call
    chat_response = requests.post(
        f"{API_BASE}/chat",
        json={"message": user_input}
    )

    if chat_response.status_code == 200:
        bot_reply = chat_response.json()["reply"]
        with st.chat_message("assistant"):
            st.write(bot_reply)
    else:
        st.error("Something went wrong talking to the backend.")