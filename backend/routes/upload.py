from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models import UploadResponse
from backend.services.rag_service import (
    split_into_chunks,
    get_embedding,
    serialize_embedding
)
from backend.services.db_service import save_document, save_chunk

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    POST/upload (multipart/form-data, not JSON)

    This endpoint is async because reading file bytes is I/O-bound.
    File(...) means the file field is required - FAstAPI returns 422 automatically if no file is attached.

    Flow:
    1. Read the uploaded file bytes
    2. Decode to text
    3. Split to text
    4. Embed each chunk (one API call per chunk)
    5. Save all chunks to SQLite
    """

    