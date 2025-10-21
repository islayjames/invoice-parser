"""
File Validation Service
Validates uploaded files for MIME type, size, and content integrity per TRD Section 7.1
"""

import magic
from fastapi import UploadFile, HTTPException

# Constants from TRD Section 7.1
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/bmp",
    "image/webp",
    "image/heic",
    "image/heif",
    "image/gif",
    "text/plain",
    "text/markdown",
}


async def validate_file(file: UploadFile) -> tuple[bytes, str]:
    """
    Validate uploaded file for size, MIME type, and content integrity.

    Args:
        file: FastAPI UploadFile instance

    Returns:
        tuple[bytes, str]: (file_content, detected_mime_type)

    Raises:
        HTTPException 400: Empty file
        HTTPException 413: File exceeds 5MB size limit
        HTTPException 415: Unsupported MIME type or MIME type mismatch
    """
    # Read file content
    content = await file.read()

    # Validate empty file
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    # Validate file size (≤5MB)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of 5MB"
        )

    # Detect actual MIME type using python-magic (magic bytes detection)
    mime = magic.Magic(mime=True)
    detected_mime = mime.from_buffer(content)

    # Generic fallback types that python-magic uses when it can't identify the file
    GENERIC_TYPES = {"application/octet-stream", "text/plain", "application/x-empty"}

    # Get declared content type from the upload
    declared_content_type = getattr(file, 'content_type', None)

    # Validate MIME type
    # If python-magic detected a specific type (not generic), it must be in allowed list
    if detected_mime not in GENERIC_TYPES:
        if detected_mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {detected_mime}"
            )

    # If python-magic returned a generic type, rely on declared content type
    else:
        if not declared_content_type or declared_content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {detected_mime}"
            )

    # Check for MIME type spoofing (content type doesn't match magic bytes)
    # Only check if python-magic detected a specific (non-generic) type
    if (declared_content_type and
        declared_content_type in ALLOWED_MIME_TYPES and
        detected_mime not in GENERIC_TYPES and
        detected_mime != declared_content_type):
        raise HTTPException(
            status_code=415,
            detail=f"MIME type mismatch: declared {declared_content_type}, detected {detected_mime}"
        )

    # Return the most specific MIME type available
    # If python-magic detected a specific type, use that
    # Otherwise, use the declared type (already validated above)
    final_mime_type = detected_mime if detected_mime not in GENERIC_TYPES else declared_content_type

    return content, final_mime_type
