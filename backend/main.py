# Assembling Everything

from fastapi import FastAPI
from backend.database import create_tables

# Import all three routers
from backend.routes.chat import router as chat_router
from backend.routes.history import router as history_router

# Create the FastAPI application instance
app = FastAPI(
    title="My Chatbot API",
    description="A simple chatbot backend with SQLite and OpenAI",
    version="1.0"
)


# This runs once when the server starts — creates DB tables if needed
@app.on_event("startup")
def startup():
    create_tables()
    print("✅ Database tables ready")

# Register each router — this is how FastAPI "knows about" your endpoints
# prefix adds a base path; tags group them in the /docs UI
# app.include_router(register_router, tags=["Registration"])
app.include_router(chat_router, tags=["Chat"])
app.include_router(history_router, tags=["History"])

# A simple health check so you can confirm the server is running
@app.get("/")
def root():
    return {"status": "API is running"}