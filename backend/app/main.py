"""
Invoice Parser API - Main Application (TRD Section 8)

FastAPI application for AI-powered invoice parsing.
Provides RESTful API endpoint for uploading and parsing invoice files.

TRD References:
- Section 8: API Design
- REQ-001: Invoice upload endpoint
- NFR-002: 99% uptime target
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.parse import router as parse_router

# Get settings instance
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Invoice Parser API starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info(f"Max File Size: {settings.max_file_size_mb}MB")

    yield

    # Shutdown
    logger.info("Invoice Parser API shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="Invoice Parser API",
    description="""
    AI-powered invoice parsing API using GPT-4o.

    **Features:**
    - Parse invoices from PDF, image, or text files
    - Extract structured data (supplier, customer, line items)
    - Confidence scoring for quality validation
    - Support for diverse invoice formats

    **Constraints:**
    - Maximum file size: 5MB
    - Processing timeout: 20 seconds
    - Critical fields require ≥50% confidence

    **Privacy:**
    - No data persistence (stateless v1)
    - Files processed in-memory only
    - No logging of invoice content
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(parse_router, tags=["Invoice Parsing"])


@app.get("/", summary="Root endpoint", tags=["Health"])
async def root():
    """
    Root endpoint - API health check.

    Returns basic API information and status.
    """
    return {
        "service": "Invoice Parser API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", summary="Health check", tags=["Health"])
async def health():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status and service information

    TRD Reference: NFR-002 - Uptime monitoring
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
        "model": settings.openai_model,
    }


# Global Error Handlers (TRD Section 7.5)


@app.exception_handler(413)
async def payload_too_large_handler(request: Request, exc):
    """Handle 413 Payload Too Large errors."""
    return JSONResponse(
        status_code=413,
        content={"detail": "File size exceeds 5MB limit. Please compress or split the document."}
    )


@app.exception_handler(415)
async def unsupported_media_type_handler(request: Request, exc):
    """Handle 415 Unsupported Media Type errors."""
    return JSONResponse(
        status_code=415,
        content={"detail": "Unsupported file format. Supported: PDF, JPEG, PNG, TIFF, BMP, WebP, HEIC, HEIF, GIF, plain text."}
    )


@app.exception_handler(422)
async def unprocessable_entity_handler(request: Request, exc):
    """Handle 422 Unprocessable Entity errors (validation failures)."""
    logger.warning(f"Validation error on {request.url}: {exc}")
    # Check if it's a Pydantic validation error
    if hasattr(exc, "errors"):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )
    # Check if it's an HTTPException with detail
    if hasattr(exc, "detail"):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.detail}
        )
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )


@app.exception_handler(504)
async def gateway_timeout_handler(request: Request, exc):
    """Handle 504 Gateway Timeout errors."""
    logger.error(f"Timeout on {request.url}: {exc}")
    return JSONResponse(
        status_code=504,
        content={"detail": "Request timeout: Processing exceeded 20 second limit. Try with a smaller or clearer file."}
    )


@app.exception_handler(503)
async def service_unavailable_handler(request: Request, exc):
    """Handle 503 Service Unavailable errors."""
    logger.error(f"Service unavailable on {request.url}: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": "Service temporarily unavailable. Please try again in a moment."}
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle 500 Internal Server Error."""
    logger.error(f"Internal error on {request.url}: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support if the problem persists."}
    )
