"""
File upload utility — handles saving uploaded images to disk with UUID filenames.
Validates file types and size limits.
"""

import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import get_settings

settings = get_settings()

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded file is an image and within size limits."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


async def save_upload_file(file: UploadFile, user_id: str) -> str:
    """
    Save an uploaded file to the uploads directory.
    Returns the relative path to the saved file.
    """
    validate_image_file(file)

    # Create user-specific upload directory
    user_dir = os.path.join(settings.UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Generate a unique filename to avoid collisions
    ext = Path(file.filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(user_dir, unique_name)

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    # Write file to disk
    with open(file_path, "wb") as f:
        f.write(content)

    # Return relative path for storage in DB
    return f"/uploads/{user_id}/{unique_name}"
