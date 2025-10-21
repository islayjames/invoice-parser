"""
Invoice Parsing API Endpoint (TRD Section 7.4)

POST /api/parse - Main endpoint for invoice file upload and parsing.

Accepts multipart/form-data file uploads, validates file format and size,
extracts structured invoice data using GPT-4o, validates confidence scores,
and returns structured JSON response.

TRD References:
- Section 7.4: API endpoint implementation
- REQ-001: File upload endpoint
- NFR-001: Parse time ≤20s
- NFR-003: Input validation (MIME, size limits)
"""

import logging
import time
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from openai import AsyncOpenAI

from app.config import get_settings
from app.services.file_validator import validate_file
from app.services.gpt4o_service import GPT4oService, InvoiceParsingError
from app.services.confidence_scorer import validate_confidence
from app.schemas import InvoiceResponse, ErrorResponse

# Get settings instance
settings = get_settings()

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


@router.post(
    "/api/parse",
    response_model=InvoiceResponse,
    responses={
        200: {"description": "Successfully parsed invoice", "model": InvoiceResponse},
        413: {"description": "Payload too large (>5MB)", "model": ErrorResponse},
        415: {"description": "Unsupported media type", "model": ErrorResponse},
        422: {"description": "Unprocessable entity (validation failed)", "model": ErrorResponse},
        504: {"description": "Gateway timeout (>20s)", "model": ErrorResponse},
        503: {"description": "Service unavailable (API error)", "model": ErrorResponse},
    },
    summary="Parse invoice file",
    description="""
    Upload an invoice file (PDF, image, or text) and receive structured JSON data.

    **Supported formats:**
    - PDF: application/pdf
    - Images: image/jpeg, image/png
    - Text: text/plain

    **Constraints:**
    - Maximum file size: 5MB
    - Processing timeout: 20 seconds
    - Critical fields must have ≥50% confidence

    **Returns:**
    Structured invoice data with supplier, customer, invoice details, line items, and metadata.
    """,
)
async def parse_invoice(
    file: UploadFile = File(..., description="Invoice file to parse (PDF, image, or text)")
) -> InvoiceResponse:
    """
    Parse uploaded invoice file into structured JSON.

    Workflow:
    1. Validate file (MIME type, size, content)
    2. Extract structured data using GPT-4o
    3. Validate confidence scores for critical fields
    4. Return InvoiceResponse or raise HTTPException

    Args:
        file: Uploaded invoice file from multipart/form-data

    Returns:
        InvoiceResponse: Structured invoice data with metadata

    Raises:
        HTTPException 413: File exceeds 5MB limit
        HTTPException 415: Unsupported MIME type
        HTTPException 422: Empty file or confidence validation failed
        HTTPException 504: Processing timeout (>20s)
        HTTPException 503: OpenAI API error or service unavailable

    TRD Reference: Section 7.4 - Parse endpoint implementation
    """
    start_time = time.time()

    try:
        # Step 1: Validate file (TRD Section 7.1)
        logger.info(f"Validating uploaded file: {file.filename}")
        file_content, mime_type = await validate_file(file)

        # Step 2: Parse invoice with GPT-4o (TRD Section 7.2)
        logger.info(f"Parsing invoice '{file.filename}' with GPT-4o")
        gpt4o_service = GPT4oService(
            openai_client=openai_client,
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            timeout=settings.openai_timeout,
        )

        invoice_response = await gpt4o_service.parse_invoice(
            file_content=file_content,
            file_name=file.filename or "unknown",
            mime_type=mime_type,
        )

        # Step 3: Validate confidence scores (TRD Section 7.3)
        logger.info(f"Validating confidence scores for '{file.filename}'")

        # Convert Pydantic model to dict for validation
        invoice_dict = invoice_response.model_dump()

        is_valid, error_message, overall_confidence = validate_confidence(invoice_dict)

        if not is_valid:
            logger.warning(
                f"Invoice '{file.filename}' rejected due to low confidence: {error_message}"
            )
            raise HTTPException(
                status_code=422,
                detail=f"Invoice quality insufficient: {error_message}"
            )

        # Step 4: Return successful response
        elapsed_time = time.time() - start_time
        logger.info(
            f"Successfully parsed '{file.filename}' in {elapsed_time:.2f}s "
            f"with confidence {overall_confidence:.2f}"
        )

        return invoice_response

    except TimeoutError as e:
        # Processing timeout (>20s)
        elapsed_time = time.time() - start_time
        logger.error(
            f"Timeout parsing '{file.filename}' after {elapsed_time:.2f}s: {str(e)}"
        )
        raise HTTPException(
            status_code=504,
            detail=f"Processing timeout: Invoice parsing exceeded {settings.openai_timeout}s limit"
        )

    except InvoiceParsingError as e:
        # GPT-4o parsing errors
        elapsed_time = time.time() - start_time
        logger.error(f"Parsing error for '{file.filename}': {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to parse invoice: {str(e)}"
        )

    except HTTPException:
        # Re-raise HTTP exceptions from confidence validation
        raise

    except Exception as e:
        # Unexpected errors
        elapsed_time = time.time() - start_time
        logger.error(
            f"Unexpected error parsing '{file.filename}' after {elapsed_time:.2f}s: "
            f"{type(e).__name__}: {str(e)}"
        )
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {type(e).__name__}"
        )
