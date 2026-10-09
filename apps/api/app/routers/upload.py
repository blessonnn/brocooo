"""File upload endpoint."""

import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException
import aiofiles

from app.config import settings

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".mp3", ".wav", ".m4a"}
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a video/audio file. Returns the storage path."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Generate unique filename
    file_id = str(uuid4())
    safe_name = f"{file_id}{ext}"
    upload_dir = os.path.join(settings.storage_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, safe_name)

    # Stream to disk
    total_size = 0
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1 MB chunks
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(413, "File too large (max 10 GB)")
            await f.write(chunk)

    return {
        "file_path": file_path,
        "filename": file.filename,
        "size": total_size,
    }
