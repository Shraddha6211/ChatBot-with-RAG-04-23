# frontend/app.py

import streamlit as st
import requests

# The base URL of your running FastAPI backend
API_BASE = "http://127.0.0.1:8000"


# ── Main Area: Chat Interface ────────────────────────────────────────────────

st.title("🤖 RAG Chatbot")
st.caption("Upload a document, then ask question about it.")

### Sidebar: Document Upload
st.sidebar.title("Upload Document")
st.sidebar.markdown("Upload a '.txt' file to give the bot knowledge about it.")

uploaded_file = st.sidebar.file_uploader(
    "Choose a text file",
    type=["txt"]
)

if uploaded_file is not None:
    # Show a button so upload only triggers on click, not on every rerender
    if st.sidebar.button("Process Document"):
        with st.sidebar.status("Processing document..."):
            # multipart/form-data upload - NOT json = 'files' parameter tells requests to send as a file upload
            response = requests.post(
                f"{API_BASE}/upload",
                files={"file": (uploaded_file.name, uploaded_file, "text/plain")}
            )
        if response.status_code ==200:
            data = response.json()
            st.sidebar.success(
                f"✅ Uploaded **{data['filename']}**\n\n"
                f"Split into **{data['chunks_stored']} chunks** and indexed."
            )
        else:
            # show the actual error from FastAPI so you can debug
            st.sidebar.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")

### Main Area: Chat

# Load chat history from the backend on every page render
history_response = requests.get(f"{API_BASE}/history")
history = history_response.json().get("history", [])

# Render all past messages as chat bubbles
for msg in history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input at the bottom
user_input = st.chat_input("Ask a question about your document...")

if user_input:
    # Show user message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Send to backend — it handles DB saving + LLM call
    with st.spinner("Searching documents and thinking..."):
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