"""
File Validation Service

Validates uploaded invoice files for MIME type, size, and content integrity.
Implements security controls defined in TRD Section 7.1 to prevent:
- Oversized file uploads (DoS protection)
- MIME type spoofing attacks
- Unsupported file format processing

Usage Example:
    ```python
    from fastapi import UploadFile
    from app.services.file_validator import validate_file

    async def process_invoice(file: UploadFile):
        # Validate file before processing
        content, mime_type = await validate_file(file)

        # Process validated content
        result = await parse_invoice(content, mime_type)
        return result
    ```

Security Controls:
    - Size Limit: 5MB maximum file size (NFR-003)
    - MIME Validation: Content-based detection using magic bytes
    - Spoofing Prevention: Comparison of declared vs. detected MIME types
    - Allowed Formats: PDF, common image formats, plain text

Performance Considerations:
    - File content read into memory (suitable for ≤5MB files)
    - python-magic performs fast magic byte inspection
    - Synchronous MIME detection (negligible overhead <100ms)
"""

import magic
from fastapi import UploadFile, HTTPException
from typing import Tuple

# Constants from TRD Section 7.1 - Security Requirements
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB (5,242,880 bytes)

# Allowed MIME types for invoice processing
# Covers: PDFs, images (common formats), and text documents
ALLOWED_MIME_TYPES = {
    # Document formats
    "application/pdf",          # Adobe PDF
    "text/plain",              # Plain text invoices
    "text/markdown",           # Markdown formatted invoices

    # Image formats (for scanned invoices)
    "image/jpeg",              # JPEG/JPG
    "image/png",               # PNG
    "image/tiff",              # TIFF (common for scans)
    "image/bmp",               # Bitmap
    "image/webp",              # WebP
    "image/heic",              # HEIC (iPhone photos)
    "image/heif",              # HEIF
    "image/gif",               # GIF
}


async def validate_file(file: UploadFile) -> Tuple[bytes, str]:
    """
    Validate uploaded file for size, MIME type, and content integrity.

    Performs three-stage validation:
    1. Size validation: Ensures file ≤5MB (DoS prevention)
    2. MIME type detection: Uses magic bytes to identify actual file type
    3. Spoofing prevention: Compares declared vs. detected MIME types

    Args:
        file: FastAPI UploadFile instance containing uploaded invoice document.
              Must have `read()` method and optional `content_type` attribute.

    Returns:
        Tuple[bytes, str]: A tuple containing:
            - bytes: Complete file content (validated, ≤5MB)
            - str: Detected MIME type (one of ALLOWED_MIME_TYPES)

    Raises:
        HTTPException:
            - 400 Bad Request: File is empty (0 bytes)
            - 413 Payload Too Large: File exceeds 5MB limit
            - 415 Unsupported Media Type: Invalid MIME type or type mismatch

    Example:
        ```python
        from fastapi import UploadFile, File

        @app.post("/parse")
        async def parse_invoice(file: UploadFile = File(...)):
            # Validate and extract content
            content, mime_type = await validate_file(file)

            # mime_type is guaranteed to be one of ALLOWED_MIME_TYPES
            # content is guaranteed to be ≤5MB
            return {"mime_type": mime_type, "size": len(content)}
        ```

    Security Notes:
        - Relies on python-magic for content-based detection (not file extension)
        - Prevents MIME type spoofing by comparing declared vs. detected types
        - All content loaded into memory (acceptable for 5MB limit)
    """
    # Stage 1: Read file content into memory
    # For 5MB limit, in-memory processing is acceptable and simplifies validation
    content = await file.read()

    # Stage 2: Empty file validation (malformed upload check)
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file '{file.filename}' is empty (0 bytes). Please upload a valid invoice document."
        )

    # Stage 3: Size limit enforcement (DoS protection - NFR-003)
    if len(content) > MAX_FILE_SIZE:
        size_mb = len(content) / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File '{file.filename}' size ({size_mb:.2f} MB) exceeds maximum allowed size of 5 MB. "
                   f"Please compress or split the document."
        )

    # Stage 4: MIME type detection using magic bytes (content-based, not filename-based)
    # python-magic reads file signatures (magic bytes) to determine actual file type
    # This is more secure than trusting file extensions or declared content types
    mime = magic.Magic(mime=True)
    detected_mime = mime.from_buffer(content)

    # Generic fallback types that python-magic returns when file signature is ambiguous
    # These require falling back to declared content type for validation
    GENERIC_TYPES = {
        "application/octet-stream",  # Generic binary data (unknown format)
        "text/plain",                # Generic text (python-magic can't determine specific format)
        "application/x-empty",       # Empty or minimal content
    }

    # Extract declared content type from multipart form upload
    # May be None if client didn't specify Content-Type header
    declared_content_type = getattr(file, 'content_type', None)

    # Stage 5: MIME type validation logic
    # Branch 1: python-magic detected a SPECIFIC file type (high confidence)
    if detected_mime not in GENERIC_TYPES:
        # Detected type must be in our allowed list
        if detected_mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type '{detected_mime}' detected in '{file.filename}'. "
                       f"Supported formats: PDF, JPEG, PNG, TIFF, BMP, WebP, HEIC, HEIF, GIF, plain text, markdown."
            )

    # Branch 2: python-magic returned GENERIC type (low confidence, ambiguous file)
    else:
        # Fall back to declared content type, but it must be present and allowed
        if not declared_content_type or declared_content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported or unrecognizable file type for '{file.filename}' (detected: {detected_mime}). "
                       f"Please ensure file has correct format and Content-Type header. "
                       f"Supported formats: PDF, JPEG, PNG, TIFF, BMP, WebP, HEIC, HEIF, GIF, plain text, markdown."
            )

    # Stage 6: MIME type spoofing prevention
    # If client declared a type AND python-magic detected a specific (non-generic) type,
    # they must match to prevent spoofing attacks (e.g., malicious .exe renamed to .pdf)
    if (declared_content_type and
        declared_content_type in ALLOWED_MIME_TYPES and
        detected_mime not in GENERIC_TYPES and
        detected_mime != declared_content_type):
        raise HTTPException(
            status_code=415,
            detail=f"MIME type mismatch for '{file.filename}': "
                   f"declared '{declared_content_type}' but actual content is '{detected_mime}'. "
                   f"This may indicate file extension spoofing."
        )

    # Stage 7: Return validated content and final MIME type
    # Prefer detected type (content-based) over declared type (client-provided)
    # Only use declared type if detection was ambiguous (generic type)
    final_mime_type = detected_mime if detected_mime not in GENERIC_TYPES else declared_content_type

    return content, final_mime_type
