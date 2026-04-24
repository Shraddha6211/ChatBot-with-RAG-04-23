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

    # Step 1 & 2: Read and decode
    # 'await' is needed here because reading bytes from an uploaded file is an asyn I/O operation in FastAPI
    try:
        contents = await file.read()
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        # The file wasn't valid UTF-8 text (might be a binary PDF)
        raise HTTPException(
            status_code=400,
            detail= "File must be a plain text (.txt) file encoded in UTF-8."
                    "For PDFs, convert to text first."
        )
    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    # Step 3: Split into chunks
    chunks = split_into_chunks(text)

    # Step 4 & 5: Save the document record, then each chunk + its embedding
    doc_id = save_document(file.filename)

    for chunk_text in chunks:
        embedding = get_embedding(chunk_text)
        embedding_str = serialize_embedding(embedding)
        save_chunk(doc_id, chunk_text, embedding_str)

    return UploadResponse(
        success= True,
        filename=file.filename,
        chunks_stored=len(chunks)
    )