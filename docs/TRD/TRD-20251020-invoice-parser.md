# Technical Requirements Document (TRD) — Invoice Parsing API & UI Prototype

## 0) Meta

* **TRD ID:** TRD-20251020-INVOICE-PARSER
* **Version:** 1.0
* **Status:** Ready for Implementation
* **Last Updated:** 2025-10-20
* **PRD Reference:** [PRD-20251020-INVOICE-PARSER v1.1](/home/james/dev/invoice-parser/docs/PRD/PRD-20251020-invoice-parser.md)
* **Technical Lead:** TBD
* **Engineering Team:** TBD
* **Target Completion:** 2 weeks from kickoff

---

## 1) Executive Summary

### 1.1) Project Overview

The Invoice Parser is an AI-powered prototype system that extracts structured data from invoice documents (PDF, images, text) using OpenAI's GPT-4o Vision API. The system provides both a RESTful API and a web-based UI for internal stakeholders to demonstrate AI-powered document processing capabilities.

**Key Technical Characteristics:**
- **Architecture**: Serverless FastAPI backend + React SPA frontend
- **AI Engine**: GPT-4o Vision API with field-level confidence scoring
- **Processing Model**: Synchronous (≤20s response time)
- **Data Model**: Stateless, no persistence (privacy-first design)
- **Deployment**: Vercel (frontend) + Railway (backend)
- **Target**: MVP/Demo for internal stakeholders

### 1.2) Technical Approach

1. **Backend Strategy**: FastAPI-based REST API with multipart file upload, GPT-4o integration via OpenAI Python SDK, Pydantic for schema validation
2. **AI Integration**: Prompt engineering for invoice field extraction with structured output format, retry logic with exponential backoff, field-level confidence scoring
3. **Frontend Strategy**: React SPA with table-based invoice display and JSON toggle, drag-and-drop file upload with FormData API
4. **Quality Strategy**: Field-level confidence scoring with critical field validation, comprehensive error handling, unit/integration/E2E testing

---

## 2) System Architecture

### 2.1) High-Level Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Frontend │◄────────┤  FastAPI Backend │◄────────┤   GPT-4o API    │
│   (Vercel)      │  HTTPS  │    (Railway)     │  HTTPS  │   (OpenAI)      │
│                 │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                            │
        │                            │
        ▼                            ▼
   User Browser              In-Memory Processing
   - Upload UI                - File Validation
   - Invoice Display          - GPT-4o Parsing
   - JSON Toggle              - Confidence Scoring
   - Copy to Clipboard        - Error Handling
                              - No Persistence
```

### 2.2) Component Architecture

#### Backend Components

```
FastAPI Application
├── main.py                    # Application entry point, CORS, middleware
├── routers/
│   └── parse.py              # POST /api/parse endpoint
├── services/
│   ├── file_validator.py     # MIME type, size, extension validation
│   ├── gpt4o_parser.py       # GPT-4o API integration with retry logic
│   └── confidence_scorer.py  # Field-level confidence analysis
├── schemas/
│   ├── invoice.py            # Pydantic models for invoice schema
│   └── error.py              # Error response models
├── utils/
│   ├── retry.py              # Exponential backoff retry decorator
│   └── logger.py             # Structured logging (metadata only)
└── config/
    └── settings.py           # Environment configuration management
```

#### Frontend Components

```
React Application
├── App.jsx                   # Main app component, routing
├── components/
│   ├── FileUpload/
│   │   ├── FileUpload.jsx    # Drag-drop + click upload
│   │   └── FileUpload.css
│   ├── InvoiceDisplay/
│   │   ├── InvoiceDisplay.jsx        # Formatted table view
│   │   ├── FormattedView.jsx         # Traditional invoice layout
│   │   ├── RawView.jsx               # Pretty-printed JSON
│   │   ├── ConfidenceWarning.jsx     # Low confidence indicator
│   │   └── InvoiceDisplay.css
│   ├── ErrorDisplay/
│   │   ├── ErrorDisplay.jsx  # Error message area
│   │   └── ErrorDisplay.css
│   └── LoadingSpinner/
│       ├── LoadingSpinner.jsx
│       └── LoadingSpinner.css
├── services/
│   └── api.js                # API client for backend calls
└── utils/
    └── clipboard.js          # Copy to clipboard utility
```

### 2.3) Data Flow

**Invoice Parsing Flow:**

1. **Upload**: User drags/selects file → Frontend validates basic constraints → POST multipart/form-data to `/api/parse`
2. **Validation**: Backend validates MIME type, size (≤5MB), extension → Rejects if invalid
3. **Processing**: Backend calls GPT-4o Vision API → Parses file with prompt → Retries on failure (3x exponential backoff)
4. **Confidence Scoring**: Backend analyzes field-level confidence → Rejects if critical fields <50% → Generates warning if 50-90%
5. **Response**: Backend returns structured JSON with confidence scores → Frontend displays formatted or raw view
6. **Cleanup**: Backend immediately deletes file from memory → No persistence

---

## 3) Technology Stack

### 3.1) Backend Stack

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Python** | 3.11+ | Programming language | Strong AI/ML library ecosystem, async support |
| **FastAPI** | 0.104+ | Web framework | Modern async framework, auto-generated OpenAPI docs, Pydantic integration |
| **Pydantic** | 2.5+ | Data validation | Type-safe schema validation, automatic JSON serialization |
| **OpenAI SDK** | 1.3+ | GPT-4o integration | Official SDK with retry logic, streaming support |
| **python-multipart** | 0.0.6+ | File upload handling | Required for FastAPI multipart form data |
| **uvicorn** | 0.24+ | ASGI server | High-performance async server for FastAPI |
| **python-magic** | 0.4+ | MIME type detection | Reliable MIME type validation beyond file extensions |
| **pytest** | 7.4+ | Testing framework | Industry standard, async support, fixtures |
| **pytest-cov** | 4.1+ | Code coverage | Coverage reporting for quality gates |
| **httpx** | 0.25+ | HTTP client | Async client for testing FastAPI endpoints |

### 3.2) Frontend Stack

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **React** | 18.2+ | UI framework | Component-based, hooks for state management |
| **Vite** | 5.0+ | Build tool | Fast dev server, optimized production builds |
| **Axios** | 1.6+ | HTTP client | Promise-based, interceptors for error handling |
| **React DnD** | 16.0+ or native | Drag-and-drop | File upload UX (or use native HTML5 API) |
| **react-json-view** | 1.21+ | JSON viewer | Pretty-printed JSON display with collapsible nodes |
| **Jest** | 29.7+ | Unit testing | React ecosystem standard |
| **React Testing Library** | 14.1+ | Component testing | User-centric testing approach |

### 3.3) Deployment & Infrastructure

| Technology | Purpose | Configuration |
|------------|---------|---------------|
| **Railway** | Backend hosting | Python runtime, environment variables for `OPENAI_API_KEY` |
| **Vercel** | Frontend hosting | Static site deployment, environment variables for backend URL |
| **GitHub** | Version control | Main branch protection, PR reviews |
| **GitHub Actions** (optional) | CI/CD | Automated testing, deployment on merge |

---

## 4) API Specifications

### 4.1) Endpoint: POST /api/parse

**Purpose**: Upload and parse an invoice file to extract structured data

**Request**:
```http
POST /api/parse HTTP/1.1
Host: <railway-backend-url>
Content-Type: multipart/form-data

Content-Disposition: form-data; name="file"; filename="invoice.pdf"
Content-Type: application/pdf

<binary file data>
```

**Request Parameters**:
- `file` (required): Invoice file (PDF, image, or text)
  - Supported MIME types: `application/pdf`, `image/jpeg`, `image/png`, `image/tiff`, `image/bmp`, `image/webp`, `image/heic`, `image/heif`, `image/gif`, `text/plain`, `text/markdown`
  - Max size: 5MB
  - Supported extensions: .pdf, .jpg, .jpeg, .png, .tiff, .tif, .bmp, .webp, .heic, .heif, .gif, .txt, .md

**Success Response** (HTTP 200):
```json
{
  "supplier": {
    "name": { "value": "Acme Corporation", "confidence": 0.98 },
    "address": { "value": "123 Main St, City, State 12345", "confidence": 0.95 },
    "phone": { "value": "+1-555-123-4567", "confidence": 0.92 },
    "email": { "value": "billing@acme.com", "confidence": 0.96 },
    "tax_id": { "value": "12-3456789", "confidence": 0.94 }
  },
  "customer": {
    "name": { "value": "Client Company Inc", "confidence": 0.97 },
    "address": { "value": "456 Oak Ave, Town, State 67890", "confidence": 0.93 },
    "account_id": { "value": "CUST-001", "confidence": 0.89 }
  },
  "invoice": {
    "number": { "value": "INV-2025-001", "confidence": 0.99 },
    "issue_date": { "value": "2025-01-15", "confidence": 0.98 },
    "due_date": { "value": "2025-02-15", "confidence": 0.98 },
    "currency": { "value": "USD", "confidence": 0.85 },
    "subtotal": { "value": 1000.00, "confidence": 0.96 },
    "tax": { "value": 80.00, "confidence": 0.94 },
    "total": { "value": 1080.00, "confidence": 0.99 },
    "payment_terms": { "value": "Net 30", "confidence": 0.91 },
    "po_number": { "value": "PO-2025-100", "confidence": 0.88 }
  },
  "line_items": [
    {
      "sku": { "value": "PROD-001", "confidence": 0.92 },
      "description": { "value": "Professional Services", "confidence": 0.95 },
      "quantity": { "value": 10, "confidence": 0.97 },
      "unit_price": { "value": 100.00, "confidence": 0.96 },
      "discount": { "value": 0.00, "confidence": 0.90 },
      "tax_rate": { "value": 0.08, "confidence": 0.88 },
      "total": { "value": 1000.00, "confidence": 0.97 }
    }
  ],
  "meta": {
    "source_file_name": "invoice.pdf",
    "source_format": "pdf",
    "model_version": "gpt-4o-2024-05-13",
    "extraction_time": "2025-10-20T14:32:10Z",
    "processing_time_ms": 8734,
    "overall_confidence": 0.88,
    "warning": "Some fields have confidence scores between 50-90%. Please review."
  }
}
```

**Error Responses**:

```json
// HTTP 413 - File Too Large
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds maximum limit of 5MB",
    "details": {
      "file_size_bytes": 6291456,
      "max_size_bytes": 5242880
    }
  }
}

// HTTP 415 - Unsupported Media Type
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "File type not supported",
    "details": {
      "detected_mime_type": "application/zip",
      "supported_types": ["application/pdf", "image/jpeg", "image/png", ...]
    }
  }
}

// HTTP 422 - Unprocessable Entity (Low Confidence)
{
  "error": {
    "code": "CONFIDENCE_TOO_LOW",
    "message": "Unable to extract required fields with sufficient confidence",
    "details": {
      "failed_fields": ["supplier.name", "invoice.total"],
      "confidence_scores": {
        "supplier.name": 0.42,
        "invoice.total": 0.38
      },
      "minimum_required": 0.50
    }
  }
}

// HTTP 504 - Gateway Timeout (GPT-4o timeout after retries)
{
  "error": {
    "code": "PROCESSING_TIMEOUT",
    "message": "Invoice processing exceeded maximum time limit",
    "details": {
      "retry_attempts": 3,
      "timeout_seconds": 20
    }
  }
}

// HTTP 503 - Service Unavailable (GPT-4o API down)
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "AI processing service temporarily unavailable",
    "details": {
      "retry_after_seconds": 60
    }
  }
}
```

### 4.2) CORS Configuration

```python
# Allow frontend origin
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "https://*.vercel.app",   # Vercel preview/production
]

cors_config = {
    "allow_origins": allowed_origins,
    "allow_credentials": False,
    "allow_methods": ["POST", "OPTIONS"],
    "allow_headers": ["Content-Type"],
    "max_age": 600
}
```

---

## 5) Data Models & Schemas

### 5.1) Pydantic Models (Backend)

```python
# schemas/invoice.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime

class FieldValue(BaseModel):
    """Base model for fields with confidence scores"""
    value: str | float | int
    confidence: float = Field(..., ge=0.0, le=1.0)

class SupplierInfo(BaseModel):
    name: FieldValue
    address: Optional[FieldValue] = None
    phone: Optional[FieldValue] = None
    email: Optional[FieldValue] = None
    tax_id: Optional[FieldValue] = None

class CustomerInfo(BaseModel):
    name: FieldValue
    address: Optional[FieldValue] = None
    account_id: Optional[FieldValue] = None

class InvoiceSummary(BaseModel):
    number: FieldValue
    issue_date: FieldValue
    due_date: FieldValue
    currency: FieldValue
    subtotal: Optional[FieldValue] = None
    tax: Optional[FieldValue] = None
    total: FieldValue
    payment_terms: Optional[FieldValue] = None
    po_number: Optional[FieldValue] = None

    @field_validator('currency')
    def default_currency(cls, v):
        if v.value is None or v.value == "":
            v.value = "USD"
        return v

class LineItem(BaseModel):
    sku: Optional[FieldValue] = None
    description: FieldValue
    quantity: FieldValue
    unit_price: FieldValue
    discount: Optional[FieldValue] = None
    tax_rate: Optional[FieldValue] = None
    total: FieldValue

class InvoiceMetadata(BaseModel):
    source_file_name: str
    source_format: Literal["pdf", "image", "text"]
    model_version: str
    extraction_time: datetime
    processing_time_ms: int
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    warning: Optional[str] = None

class InvoiceResponse(BaseModel):
    supplier: SupplierInfo
    customer: CustomerInfo
    invoice: InvoiceSummary
    line_items: List[LineItem] = Field(default_factory=list, max_length=50)
    meta: InvoiceMetadata

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    error: ErrorDetail
```

### 5.2) Critical Field Validation Logic

```python
# services/confidence_scorer.py

from typing import Dict, List, Tuple

CRITICAL_FIELDS = [
    ("supplier", "name"),
    ("invoice", "number"),
    ("invoice", "issue_date"),
    ("invoice", "due_date"),
    ("invoice", "total"),
    ("customer", "name"),
]

CONFIDENCE_THRESHOLD_REJECT = 0.50
CONFIDENCE_THRESHOLD_WARNING = 0.90

def validate_confidence(invoice_data: dict) -> Tuple[bool, Optional[str], float]:
    """
    Validate confidence scores and return (is_valid, warning_message, overall_confidence)

    Returns:
        - is_valid: False if any critical field <50%, True otherwise
        - warning_message: Non-empty if any field triggers warning
        - overall_confidence: Minimum confidence across all critical fields
    """
    failed_fields = []
    warning_fields = []
    min_confidence = 1.0

    # Check critical fields
    for section, field in CRITICAL_FIELDS:
        field_data = invoice_data.get(section, {}).get(field)
        if field_data is None:
            failed_fields.append(f"{section}.{field}")
            min_confidence = 0.0
            continue

        confidence = field_data.get("confidence", 0.0)
        min_confidence = min(min_confidence, confidence)

        if confidence < CONFIDENCE_THRESHOLD_REJECT:
            failed_fields.append(f"{section}.{field}")
        elif confidence < CONFIDENCE_THRESHOLD_WARNING:
            warning_fields.append(f"{section}.{field}")

    # Check non-critical fields that are present
    for section in ["supplier", "customer", "invoice"]:
        for field, value in invoice_data.get(section, {}).items():
            if (section, field) in CRITICAL_FIELDS:
                continue
            if value is not None and isinstance(value, dict):
                confidence = value.get("confidence", 0.0)
                if confidence < CONFIDENCE_THRESHOLD_WARNING:
                    warning_fields.append(f"{section}.{field}")

    # Determine result
    if failed_fields:
        return False, None, min_confidence

    warning_message = None
    if warning_fields:
        warning_message = f"Some fields have confidence scores between 50-90%. Please review: {', '.join(warning_fields)}"

    return True, warning_message, min_confidence
```

---

## 6) GPT-4o Integration Architecture

### 6.1) Prompt Engineering Strategy

```python
# services/gpt4o_parser.py

INVOICE_EXTRACTION_PROMPT = """
You are an expert invoice data extraction system. Extract all relevant fields from the provided invoice document.

CRITICAL INSTRUCTIONS:
1. Extract ALL visible text and data from the invoice
2. For each field, provide both the extracted value AND a confidence score (0.0 to 1.0)
3. Use confidence scores based on:
   - Text clarity/readability (higher = clearer)
   - Field label presence (higher = explicit label found)
   - Data format validity (higher = matches expected format)
4. For dates, convert to YYYY-MM-DD format (assume MM/DD/YYYY if ambiguous)
5. If currency is not explicitly stated, assume "USD"
6. Extract up to 50 line items maximum
7. For English invoices, extract as-is. For Spanish invoices, translate field names to English but keep values in original language with translation notes.

REQUIRED FIELDS (must extract with confidence ≥0.5):
- supplier.name
- customer.name
- invoice.number
- invoice.issue_date
- invoice.due_date
- invoice.total

Return ONLY valid JSON matching this exact schema:
{schema_json}

Do not include any explanatory text, only the JSON object.
"""

async def parse_invoice_with_gpt4o(
    file_content: bytes,
    file_name: str,
    mime_type: str,
    openai_client: OpenAI
) -> dict:
    """
    Parse invoice using GPT-4o Vision API with structured output

    Args:
        file_content: Raw file bytes
        file_name: Original filename
        mime_type: Detected MIME type
        openai_client: Initialized OpenAI client

    Returns:
        Parsed invoice data as dictionary

    Raises:
        ValueError: If GPT-4o returns invalid JSON
        OpenAIError: If API call fails after retries
    """
    # Encode file for GPT-4o Vision API
    if mime_type.startswith("image/"):
        base64_content = base64.b64encode(file_content).decode()
        content_type = mime_type
    elif mime_type == "application/pdf":
        # Convert PDF first page to image using pdf2image or PyMuPDF
        base64_content = convert_pdf_to_base64_image(file_content)
        content_type = "image/png"
    else:  # text
        text_content = file_content.decode('utf-8')
        # For text, use standard GPT-4o (not Vision)
        return await parse_text_invoice(text_content, openai_client)

    # Prepare schema for prompt
    schema_json = InvoiceResponse.model_json_schema()
    prompt = INVOICE_EXTRACTION_PROMPT.format(schema_json=json.dumps(schema_json, indent=2))

    # Call GPT-4o Vision API with retry logic
    response = await retry_with_exponential_backoff(
        lambda: openai_client.chat.completions.create(
            model="gpt-4o",
            temperature=0.4,
            max_tokens=4096,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise invoice data extraction system. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{base64_content}"
                            }
                        }
                    ]
                }
            ]
        ),
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0
    )

    # Parse and validate response
    raw_json = response.choices[0].message.content
    invoice_data = json.loads(raw_json)

    # Add metadata
    invoice_data["meta"] = {
        "source_file_name": file_name,
        "source_format": get_format_type(mime_type),
        "model_version": response.model,
        "extraction_time": datetime.utcnow().isoformat() + "Z",
    }

    return invoice_data
```

### 6.2) Retry Logic with Exponential Backoff

```python
# utils/retry.py

import asyncio
import logging
from typing import Callable, TypeVar
from openai import OpenAIError, RateLimitError, APITimeoutError

T = TypeVar('T')
logger = logging.getLogger(__name__)

async def retry_with_exponential_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
) -> T:
    """
    Retry async function with exponential backoff

    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for each retry (default: 2.0)
        jitter: Add random jitter to prevent thundering herd (default: True)

    Returns:
        Result from successful function call

    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except (RateLimitError, APITimeoutError, OpenAIError) as e:
            last_exception = e

            if attempt == max_retries:
                logger.error(f"All {max_retries} retries failed: {e}")
                raise

            # Calculate delay with optional jitter
            actual_delay = delay
            if jitter:
                import random
                actual_delay = delay * (0.5 + random.random())

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                f"Retrying in {actual_delay:.2f}s..."
            )

            await asyncio.sleep(actual_delay)
            delay *= backoff_factor

    raise last_exception
```

---

## 7) Security & Privacy Architecture

### 7.1) Input Validation

```python
# services/file_validator.py

import magic
from fastapi import UploadFile, HTTPException

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

MIME_TO_EXTENSIONS = {
    "application/pdf": [".pdf"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/tiff": [".tiff", ".tif"],
    "image/bmp": [".bmp"],
    "image/webp": [".webp"],
    "image/heic": [".heic"],
    "image/heif": [".heif"],
    "image/gif": [".gif"],
    "text/plain": [".txt"],
    "text/markdown": [".md"],
}

async def validate_file(file: UploadFile) -> tuple[bytes, str]:
    """
    Validate uploaded file and return content + MIME type

    Returns:
        (file_content_bytes, detected_mime_type)

    Raises:
        HTTPException: 413 if too large, 415 if unsupported type
    """
    # Read file content
    content = await file.read()

    # Validate size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB",
                    "details": {
                        "file_size_bytes": len(content),
                        "max_size_bytes": MAX_FILE_SIZE
                    }
                }
            }
        )

    # Detect MIME type (use python-magic for reliable detection)
    mime = magic.Magic(mime=True)
    detected_mime = mime.from_buffer(content)

    # Validate MIME type
    if detected_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail={
                "error": {
                    "code": "UNSUPPORTED_FILE_TYPE",
                    "message": "File type not supported",
                    "details": {
                        "detected_mime_type": detected_mime,
                        "supported_types": list(ALLOWED_MIME_TYPES)
                    }
                }
            }
        )

    # Validate extension matches MIME type
    file_extension = Path(file.filename).suffix.lower()
    expected_extensions = MIME_TO_EXTENSIONS.get(detected_mime, [])

    if expected_extensions and file_extension not in expected_extensions:
        logger.warning(
            f"File extension mismatch: {file_extension} doesn't match "
            f"detected MIME type {detected_mime}"
        )
        # Allow but log warning (extension spoofing attempt)

    return content, detected_mime
```

### 7.2) Privacy & Data Handling

```python
# routers/parse.py

from contextlib import asynccontextmanager

@asynccontextmanager
async def secure_file_handling(file_content: bytes):
    """
    Context manager ensuring file content is deleted after processing
    """
    try:
        yield file_content
    finally:
        # Explicitly delete from memory
        del file_content
        # Force garbage collection (optional but explicit)
        import gc
        gc.collect()

@router.post("/api/parse")
async def parse_invoice(file: UploadFile = File(...)):
    """
    Parse invoice endpoint with privacy-first design
    """
    start_time = time.time()

    # Validate file (raises HTTPException on failure)
    file_content, mime_type = await validate_file(file)

    # Process with secure handling
    async with secure_file_handling(file_content):
        try:
            # Parse invoice
            invoice_data = await parse_invoice_with_gpt4o(
                file_content,
                file.filename,
                mime_type,
                openai_client
            )

            # Validate confidence scores
            is_valid, warning, overall_conf = validate_confidence(invoice_data)

            if not is_valid:
                # Critical fields failed confidence threshold
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": {
                            "code": "CONFIDENCE_TOO_LOW",
                            "message": "Unable to extract required fields with sufficient confidence",
                            "details": {
                                "failed_fields": get_failed_fields(invoice_data),
                                "minimum_required": 0.50
                            }
                        }
                    }
                )

            # Add metadata
            processing_time = int((time.time() - start_time) * 1000)
            invoice_data["meta"]["processing_time_ms"] = processing_time
            invoice_data["meta"]["overall_confidence"] = overall_conf
            invoice_data["meta"]["warning"] = warning

            # Validate with Pydantic
            response = InvoiceResponse(**invoice_data)

            # Log metadata only (NO invoice content)
            logger.info(
                "Invoice parsed successfully",
                extra={
                    "file_name": file.filename,
                    "mime_type": mime_type,
                    "processing_time_ms": processing_time,
                    "overall_confidence": overall_conf,
                    "has_warning": warning is not None
                }
            )

            return response

        except Exception as e:
            # Log error without invoice content
            logger.error(
                "Invoice parsing failed",
                extra={
                    "file_name": file.filename,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise

    # file_content is deleted when exiting context manager
```

---

## 8) Frontend Architecture

### 8.1) Component Structure

```javascript
// App.jsx
import { useState } from 'react';
import FileUpload from './components/FileUpload/FileUpload';
import InvoiceDisplay from './components/InvoiceDisplay/InvoiceDisplay';
import ErrorDisplay from './components/ErrorDisplay/ErrorDisplay';
import LoadingSpinner from './components/LoadingSpinner/LoadingSpinner';
import { parseInvoice } from './services/api';

function App() {
  const [invoiceData, setInvoiceData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setInvoiceData(null);

    try {
      const data = await parseInvoice(file);
      setInvoiceData(data);
    } catch (err) {
      setError(err.response?.data?.error || {
        code: 'UNKNOWN_ERROR',
        message: err.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Invoice Parser Demo</h1>
      </header>

      <main>
        <FileUpload onFileSelect={handleFileUpload} disabled={loading} />

        {loading && <LoadingSpinner />}
        {error && <ErrorDisplay error={error} />}
        {invoiceData && <InvoiceDisplay data={invoiceData} />}
      </main>
    </div>
  );
}

export default App;
```

```javascript
// components/InvoiceDisplay/InvoiceDisplay.jsx
import { useState } from 'react';
import FormattedView from './FormattedView';
import RawView from './RawView';
import ConfidenceWarning from './ConfidenceWarning';
import { copyToClipboard } from '../../utils/clipboard';

function InvoiceDisplay({ data }) {
  const [viewMode, setViewMode] = useState('formatted'); // 'formatted' | 'raw'

  const handleCopy = async () => {
    try {
      await copyToClipboard(JSON.stringify(data, null, 2));
      alert('Copied to clipboard!');
    } catch (err) {
      alert('Failed to copy: ' + err.message);
    }
  };

  return (
    <div className="invoice-display">
      <div className="controls">
        <button
          onClick={() => setViewMode('formatted')}
          className={viewMode === 'formatted' ? 'active' : ''}
        >
          Formatted View
        </button>
        <button
          onClick={() => setViewMode('raw')}
          className={viewMode === 'raw' ? 'active' : ''}
        >
          Raw JSON
        </button>
        <button onClick={handleCopy} className="copy-btn">
          📋 Copy JSON
        </button>
      </div>

      {data.meta?.warning && <ConfidenceWarning message={data.meta.warning} />}

      {viewMode === 'formatted' ? (
        <FormattedView data={data} />
      ) : (
        <RawView data={data} />
      )}
    </div>
  );
}

export default InvoiceDisplay;
```

```javascript
// components/InvoiceDisplay/FormattedView.jsx
function FormattedView({ data }) {
  const { supplier, customer, invoice, line_items } = data;

  return (
    <div className="formatted-view">
      {/* Invoice Header */}
      <div className="invoice-header">
        <div className="supplier-info">
          <h2>{supplier.name.value}</h2>
          <p>{supplier.address?.value}</p>
          <p>{supplier.phone?.value}</p>
          <p>{supplier.email?.value}</p>
          {supplier.tax_id?.value && <p>Tax ID: {supplier.tax_id.value}</p>}
        </div>

        <div className="invoice-details">
          <h3>INVOICE</h3>
          <p><strong>Invoice #:</strong> {invoice.number.value}</p>
          <p><strong>Date:</strong> {invoice.issue_date.value}</p>
          <p><strong>Due Date:</strong> {invoice.due_date.value}</p>
          {invoice.po_number?.value && <p><strong>PO #:</strong> {invoice.po_number.value}</p>}
        </div>
      </div>

      {/* Bill To */}
      <div className="customer-info">
        <h4>Bill To:</h4>
        <p><strong>{customer.name.value}</strong></p>
        <p>{customer.address?.value}</p>
        {customer.account_id?.value && <p>Account: {customer.account_id.value}</p>}
      </div>

      {/* Line Items Table */}
      {line_items && line_items.length > 0 && (
        <table className="line-items-table">
          <thead>
            <tr>
              <th>Description</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {line_items.map((item, idx) => (
              <tr key={idx}>
                <td>{item.description.value}</td>
                <td>{item.quantity.value}</td>
                <td>${item.unit_price.value.toFixed(2)}</td>
                <td>${item.total.value.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Payment Summary */}
      <div className="payment-summary">
        {invoice.subtotal?.value && (
          <p><strong>Subtotal:</strong> ${invoice.subtotal.value.toFixed(2)}</p>
        )}
        {invoice.tax?.value && (
          <p><strong>Tax:</strong> ${invoice.tax.value.toFixed(2)}</p>
        )}
        <p className="total"><strong>Total:</strong> ${invoice.total.value.toFixed(2)} {invoice.currency.value}</p>
        {invoice.payment_terms?.value && (
          <p className="terms">Payment Terms: {invoice.payment_terms.value}</p>
        )}
      </div>
    </div>
  );
}

export default FormattedView;
```

### 8.2) API Client

```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 25000, // 25s (slightly more than backend 20s limit)
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});

export async function parseInvoice(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/api/parse', formData);
  return response.data;
}
```

---

## 9) Testing Strategy

### 9.1) Test Dataset

**Location**: `tests/fixtures/invoices/`

**Contents**:
- 10-20 clean PDF invoice samples
- Various layouts: service invoices, product invoices, mixed
- Various vendors: different templates and formats
- Ground truth JSON files for each sample (manually verified)

**Example Ground Truth**:
```json
// tests/fixtures/invoices/sample-001-ground-truth.json
{
  "file_name": "sample-001.pdf",
  "expected_fields": {
    "supplier.name": "Acme Corporation",
    "invoice.number": "INV-2025-001",
    "invoice.total": 1080.00,
    "invoice.issue_date": "2025-01-15",
    "invoice.due_date": "2025-02-15",
    "customer.name": "Client Company Inc"
  },
  "expected_line_items_count": 1
}
```

### 9.2) Backend Testing

```python
# tests/test_parse_endpoint.py

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

@pytest.mark.asyncio
async def test_parse_valid_pdf_invoice(test_client, sample_invoice_pdf):
    """Test successful parsing of clean PDF invoice"""
    files = {"file": ("invoice.pdf", sample_invoice_pdf, "application/pdf")}
    response = test_client.post("/api/parse", files=files)

    assert response.status_code == 200
    data = response.json()

    # Validate schema
    assert "supplier" in data
    assert "customer" in data
    assert "invoice" in data
    assert "meta" in data

    # Validate critical fields
    assert data["supplier"]["name"]["confidence"] >= 0.5
    assert data["invoice"]["total"]["confidence"] >= 0.5
    assert data["meta"]["processing_time_ms"] <= 20000

@pytest.mark.asyncio
async def test_file_too_large(test_client):
    """Test rejection of files >5MB"""
    large_file = b"x" * (6 * 1024 * 1024)  # 6MB
    files = {"file": ("large.pdf", large_file, "application/pdf")}
    response = test_client.post("/api/parse", files=files)

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"

@pytest.mark.asyncio
async def test_unsupported_file_type(test_client):
    """Test rejection of unsupported MIME types"""
    zip_file = b"PK\x03\x04..."  # ZIP file signature
    files = {"file": ("archive.zip", zip_file, "application/zip")}
    response = test_client.post("/api/parse", files=files)

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"

@pytest.mark.asyncio
async def test_confidence_scoring_accuracy(test_client, test_dataset):
    """Test field extraction accuracy across test dataset"""
    results = []

    for sample in test_dataset:
        files = {"file": (sample["file_name"], sample["content"], "application/pdf")}
        response = test_client.post("/api/parse", files=files)

        if response.status_code == 200:
            data = response.json()
            ground_truth = sample["ground_truth"]

            # Compare extracted values to ground truth
            accuracy = calculate_field_accuracy(data, ground_truth)
            results.append(accuracy)

    # Assert ≥90% accuracy across dataset
    avg_accuracy = sum(results) / len(results)
    assert avg_accuracy >= 0.90, f"Average accuracy {avg_accuracy:.2%} below 90% threshold"
```

### 9.3) Frontend Testing

```javascript
// tests/InvoiceDisplay.test.jsx

import { render, screen, fireEvent } from '@testing-library/react';
import InvoiceDisplay from '../components/InvoiceDisplay/InvoiceDisplay';

const mockInvoiceData = {
  supplier: { name: { value: "Acme Corp", confidence: 0.98 } },
  customer: { name: { value: "Client Inc", confidence: 0.97 } },
  invoice: {
    number: { value: "INV-001", confidence: 0.99 },
    total: { value: 1000.00, confidence: 0.95 },
    issue_date: { value: "2025-01-15", confidence: 0.98 },
    due_date: { value: "2025-02-15", confidence: 0.98 },
    currency: { value: "USD", confidence: 0.85 }
  },
  line_items: [],
  meta: {
    source_file_name: "test.pdf",
    source_format: "pdf",
    model_version: "gpt-4o",
    extraction_time: "2025-10-20T14:00:00Z",
    processing_time_ms: 5000,
    overall_confidence: 0.95,
    warning: null
  }
};

test('renders formatted view by default', () => {
  render(<InvoiceDisplay data={mockInvoiceData} />);

  expect(screen.getByText('Acme Corp')).toBeInTheDocument();
  expect(screen.getByText(/INV-001/)).toBeInTheDocument();
  expect(screen.getByText(/\$1000\.00/)).toBeInTheDocument();
});

test('toggles to raw JSON view', () => {
  render(<InvoiceDisplay data={mockInvoiceData} />);

  const rawButton = screen.getByText('Raw JSON');
  fireEvent.click(rawButton);

  // Should show JSON structure
  expect(screen.getByText(/"supplier"/)).toBeInTheDocument();
});

test('copies JSON to clipboard', async () => {
  Object.assign(navigator, {
    clipboard: {
      writeText: jest.fn(() => Promise.resolve()),
    },
  });

  render(<InvoiceDisplay data={mockInvoiceData} />);

  const copyButton = screen.getByText(/Copy JSON/);
  fireEvent.click(copyButton);

  expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
    expect.stringContaining('"supplier"')
  );
});

test('displays warning for low confidence', () => {
  const dataWithWarning = {
    ...mockInvoiceData,
    meta: { ...mockInvoiceData.meta, warning: "Low confidence detected" }
  };

  render(<InvoiceDisplay data={dataWithWarning} />);

  expect(screen.getByText(/Low confidence detected/)).toBeInTheDocument();
});
```

### 9.4) E2E Testing

```javascript
// tests/e2e/invoice-parsing.spec.js (Playwright)

import { test, expect } from '@playwright/test';
import path from 'path';

test('complete invoice parsing workflow', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Upload file
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(path.join(__dirname, '../fixtures/sample-001.pdf'));

  // Wait for loading spinner
  await expect(page.locator('.loading-spinner')).toBeVisible();

  // Wait for results (max 25s)
  await expect(page.locator('.invoice-display')).toBeVisible({ timeout: 25000 });

  // Verify formatted view shows invoice data
  await expect(page.locator('text=INVOICE')).toBeVisible();
  await expect(page.locator('text=/INV-\\d+/')).toBeVisible();

  // Toggle to raw JSON
  await page.click('text=Raw JSON');
  await expect(page.locator('text="supplier"')).toBeVisible();

  // Copy to clipboard
  await page.click('text=Copy JSON');
  await expect(page.locator('text=/Copied/')).toBeVisible();
});

test('error handling for invalid file', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Upload invalid file (too large)
  const largeFile = Buffer.alloc(6 * 1024 * 1024); // 6MB
  await page.locator('input[type="file"]').setInputFiles({
    name: 'large.pdf',
    mimeType: 'application/pdf',
    buffer: largeFile
  });

  // Should show error
  await expect(page.locator('.error-display')).toBeVisible({ timeout: 5000 });
  await expect(page.locator('text=/File size exceeds/')).toBeVisible();
});
```

---

## 10) Deployment Architecture

### 10.1) Backend Deployment (Railway)

**Configuration** (`railway.json` or GUI):
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Environment Variables**:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4o access
- `PORT`: Auto-assigned by Railway
- `CORS_ORIGINS`: Frontend URL (e.g., `https://invoice-parser.vercel.app`)
- `LOG_LEVEL`: `INFO` (or `DEBUG` for troubleshooting)

**Requirements** (`requirements.txt`):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
openai==1.3.0
python-multipart==0.0.6
python-magic==0.4.27
Pillow==10.1.0
PyMuPDF==1.23.8
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
```

### 10.2) Frontend Deployment (Vercel)

**Configuration** (`vercel.json`):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_BASE_URL": "@api-base-url"
  }
}
```

**Environment Variables**:
- `VITE_API_BASE_URL`: Railway backend URL (e.g., `https://invoice-parser-backend.railway.app`)

**Build Settings**:
- Framework: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`
- Node.js Version: 18.x

### 10.3) Local Development

**Backend**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-..."
export CORS_ORIGINS="http://localhost:5173"

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
# Install dependencies
npm install

# Set environment variables (.env.local)
VITE_API_BASE_URL=http://localhost:8000

# Run development server
npm run dev
```

---

## 11) Master Task List

**Project Status**: 🔴 Not Started | **Total Tasks**: 38 | **Completed**: 0 | **Remaining**: 38

### Task Summary by Category
- [ ] **Foundation Tasks**: 6 tasks (0 completed)
- [ ] **Backend Development**: 14 tasks (0 completed)
- [ ] **Frontend Development**: 9 tasks (0 completed)
- [ ] **Testing & Quality**: 7 tasks (0 completed)
- [ ] **Deployment**: 2 tasks (0 completed)

### All Tasks (Detailed)

#### Foundation Tasks (6 tasks)

- [ ] **TRD-001**: Project setup and repository initialization (2h) - Priority: High
  - Initialize Git repository with `.gitignore` (Python, Node, env files)
  - Create project structure (`backend/`, `frontend/`, `tests/`, `docs/`)
  - Set up README.md with project overview and setup instructions

- [ ] **TRD-002**: Backend environment setup (3h) - Priority: High - Depends: TRD-001
  - Create Python virtual environment
  - Install FastAPI, Uvicorn, OpenAI SDK, and dependencies
  - Create `requirements.txt` and `requirements-dev.txt`
  - Set up `.env.example` with required environment variables

- [ ] **TRD-003**: Frontend environment setup (2h) - Priority: High - Depends: TRD-001
  - Initialize Vite + React project
  - Install dependencies (Axios, react-json-view)
  - Configure Vite for development and production
  - Create `.env.example` with API base URL

- [ ] **TRD-004**: Testing framework setup (3h) - Priority: High - Depends: TRD-002
  - Configure pytest with async support
  - Set up pytest-cov for coverage reporting
  - Create test fixtures directory with sample invoices
  - Configure Jest and React Testing Library for frontend

- [ ] **TRD-005**: Logging and monitoring setup (2h) - Priority: Medium - Depends: TRD-002
  - Configure structured logging (metadata only, no invoice content)
  - Set up log levels (DEBUG for dev, INFO for production)
  - Add request/response logging middleware (exclude sensitive data)

- [ ] **TRD-006**: Test dataset creation (4h) - Priority: High
  - Collect 10-20 clean PDF invoice samples (various layouts)
  - Create ground truth JSON files for each sample
  - Document expected fields and accuracy thresholds
  - Store in `tests/fixtures/invoices/` directory

#### Backend Development Tasks (14 tasks)

- [ ] **TRD-007**: FastAPI application structure (2h) - Priority: High - Depends: TRD-002
  - Create `main.py` with FastAPI app initialization
  - Configure CORS middleware with allowed origins
  - Add health check endpoint (`GET /health`)
  - Set up application startup/shutdown events

- [ ] **TRD-008**: Pydantic data models (3h) - Priority: High - Depends: TRD-007
  - Implement `FieldValue`, `SupplierInfo`, `CustomerInfo` models
  - Implement `InvoiceSummary`, `LineItem`, `InvoiceMetadata` models
  - Implement `InvoiceResponse` and `ErrorResponse` models
  - Add field validators (currency default, date format, confidence range)

- [ ] **TRD-009**: File validation service (4h) - Priority: High - Depends: TRD-007
  - Implement `validate_file()` with MIME type detection (python-magic)
  - Add file size validation (≤5MB, return HTTP 413 if exceeded)
  - Add MIME type whitelist validation (return HTTP 415 if unsupported)
  - Add extension matching validation with logging

- [ ] **TRD-010**: Retry logic utility (2h) - Priority: High - Depends: TRD-007
  - Implement `retry_with_exponential_backoff()` function
  - Configure 3 retries with 1s initial delay, 2x backoff
  - Add jitter to prevent thundering herd
  - Handle OpenAI-specific exceptions (RateLimitError, APITimeoutError)

- [ ] **TRD-011**: GPT-4o integration service (6h) - Priority: High - Depends: TRD-008, TRD-010
  - Implement `parse_invoice_with_gpt4o()` function
  - Create invoice extraction prompt with schema injection
  - Handle PDF → image conversion (PyMuPDF or pdf2image)
  - Handle image base64 encoding for Vision API
  - Handle text file direct parsing
  - Integrate retry logic for API calls
  - Parse and validate JSON response

- [ ] **TRD-012**: Confidence scoring service (4h) - Priority: High - Depends: TRD-008
  - Implement `validate_confidence()` function
  - Define critical fields list (supplier.name, invoice.number, etc.)
  - Check critical fields ≥50% (reject if failed)
  - Check all fields for warning threshold (50-90% or <90% non-critical)
  - Calculate overall confidence (min across critical fields)
  - Generate warning messages

- [ ] **TRD-013**: Parse endpoint implementation (4h) - Priority: High - Depends: TRD-009, TRD-011, TRD-012
  - Implement `POST /api/parse` endpoint with file upload
  - Integrate file validation
  - Integrate GPT-4o parsing service
  - Integrate confidence scoring validation
  - Add secure file handling context manager (immediate deletion)
  - Add processing time tracking
  - Add metadata-only logging (no invoice content)

- [ ] **TRD-014**: Error handling implementation (3h) - Priority: High - Depends: TRD-013
  - Implement error response formatting (JSON with code, message, details)
  - Add HTTP 413 handler for file too large
  - Add HTTP 415 handler for unsupported file type
  - Add HTTP 422 handler for low confidence
  - Add HTTP 504 handler for GPT-4o timeout
  - Add HTTP 503 handler for service unavailable
  - Add global exception handler for unexpected errors

- [ ] **TRD-015**: Backend unit tests (5h) - Priority: High - Depends: TRD-013
  - Test file validation (size, MIME type, extension)
  - Test confidence scoring logic (critical fields, thresholds)
  - Test retry logic (exponential backoff, max retries)
  - Test Pydantic model validation
  - Achieve ≥80% code coverage

- [ ] **TRD-016**: Backend integration tests (4h) - Priority: High - Depends: TRD-013
  - Test `/api/parse` with valid PDF invoices
  - Test error scenarios (file too large, unsupported type)
  - Test GPT-4o integration with mocked responses
  - Test end-to-end parsing flow with test dataset samples

- [ ] **TRD-017**: Performance optimization (3h) - Priority: Medium - Depends: TRD-013
  - Profile parse endpoint for bottlenecks
  - Optimize image encoding/processing
  - Add async file reading where possible
  - Verify ≤20s response time for 5MB files

- [ ] **TRD-018**: Backend API documentation (2h) - Priority: Medium - Depends: TRD-013
  - Configure FastAPI OpenAPI/Swagger UI
  - Add endpoint descriptions and examples
  - Document error responses
  - Add request/response schemas

- [ ] **TRD-019**: Security hardening (3h) - Priority: High - Depends: TRD-014
  - Review CORS configuration for production
  - Add request size limits at app level
  - Validate environment variable presence on startup
  - Add security headers (X-Content-Type-Options, etc.)

- [ ] **TRD-020**: Backend configuration management (2h) - Priority: High - Depends: TRD-007
  - Create `config/settings.py` with Pydantic Settings
  - Load environment variables with validation
  - Add configuration for CORS, file limits, GPT-4o settings
  - Add development vs production config profiles

#### Frontend Development Tasks (9 tasks)

- [ ] **TRD-021**: React application structure (2h) - Priority: High - Depends: TRD-003
  - Create `App.jsx` with main layout
  - Set up component directory structure
  - Add basic CSS structure and variables
  - Configure routing (if needed for multi-page)

- [ ] **TRD-022**: FileUpload component (3h) - Priority: High - Depends: TRD-021
  - Implement drag-and-drop zone with visual feedback
  - Implement click-to-browse file input
  - Add client-side validation (file size, extensions)
  - Add file preview (filename, size)
  - Style with basic CSS

- [ ] **TRD-023**: LoadingSpinner component (1h) - Priority: Medium - Depends: TRD-021
  - Create spinner component with animation
  - Add loading message ("Processing invoice...")
  - Style for center alignment and visibility

- [ ] **TRD-024**: ErrorDisplay component (2h) - Priority: High - Depends: TRD-021
  - Display error code and message
  - Show error details if available
  - Style with error color scheme (red/orange)
  - Add dismiss/retry functionality

- [ ] **TRD-025**: FormattedView component (4h) - Priority: High - Depends: TRD-021
  - Implement traditional invoice layout (header, bill-to, line items, total)
  - Display supplier info in header
  - Display customer "Bill To" section
  - Render line items table with columns (description, qty, price, total)
  - Display payment summary (subtotal, tax, total, terms)
  - Style to match traditional invoice format

- [ ] **TRD-026**: RawView component (2h) - Priority: High - Depends: TRD-021
  - Integrate react-json-view for JSON display
  - Configure pretty-printing and collapsible nodes
  - Style for readability (monospace font, syntax highlighting)

- [ ] **TRD-027**: InvoiceDisplay component (3h) - Priority: High - Depends: TRD-025, TRD-026
  - Implement view toggle (formatted vs raw)
  - Add ConfidenceWarning subcomponent for low confidence alerts
  - Implement copy-to-clipboard functionality
  - Manage view state (useState hook)

- [ ] **TRD-028**: API client service (2h) - Priority: High - Depends: TRD-021
  - Create Axios client with base URL configuration
  - Implement `parseInvoice(file)` function with FormData
  - Configure timeout (25s to accommodate backend 20s limit)
  - Add error handling and response transformation

- [ ] **TRD-029**: Frontend integration and state management (3h) - Priority: High - Depends: TRD-022, TRD-024, TRD-027, TRD-028
  - Wire up FileUpload → API call → InvoiceDisplay flow
  - Manage global state (loading, error, invoiceData)
  - Add error handling for network failures
  - Test complete user workflow

#### Testing & Quality Tasks (7 tasks)

- [ ] **TRD-030**: Frontend unit tests (4h) - Priority: High - Depends: TRD-029
  - Test FileUpload component (file selection, validation)
  - Test InvoiceDisplay component (view toggle, copy to clipboard)
  - Test FormattedView rendering with mock data
  - Test RawView JSON display
  - Test ErrorDisplay with various error types

- [ ] **TRD-031**: Frontend integration tests (3h) - Priority: High - Depends: TRD-029
  - Test complete upload → display workflow with mocked API
  - Test error scenarios (API errors, network failures)
  - Test loading states and transitions

- [ ] **TRD-032**: E2E tests with Playwright (5h) - Priority: High - Depends: TRD-029, TRD-016
  - Set up Playwright test environment
  - Test complete invoice parsing workflow (upload → parse → display)
  - Test view toggling and copy to clipboard
  - Test error handling for invalid files
  - Test with multiple invoice samples from test dataset

- [ ] **TRD-033**: Accuracy validation against test dataset (4h) - Priority: High - Depends: TRD-016, TRD-006
  - Run parsing on all test dataset samples
  - Compare extracted fields to ground truth
  - Calculate field-level accuracy percentages
  - Generate accuracy report
  - Validate ≥90% accuracy threshold

- [ ] **TRD-034**: Performance testing (3h) - Priority: High - Depends: TRD-016
  - Test parse time for various file sizes (1MB, 3MB, 5MB)
  - Test with different file formats (PDF, JPEG, PNG)
  - Validate ≤20s response time for all samples
  - Profile bottlenecks if exceeding threshold

- [ ] **TRD-035**: Code coverage analysis (2h) - Priority: Medium - Depends: TRD-015, TRD-030
  - Run pytest-cov on backend tests
  - Run Jest coverage on frontend tests
  - Validate ≥80% backend coverage, ≥70% frontend coverage
  - Identify untested code paths and add tests if critical

- [ ] **TRD-036**: Security testing (3h) - Priority: High - Depends: TRD-019
  - Test file upload with malicious files (path traversal attempts)
  - Test MIME type spoofing (wrong extension for type)
  - Test CORS enforcement with different origins
  - Test oversized file rejection
  - Review for common vulnerabilities (OWASP Top 10)

#### Deployment Tasks (2 tasks)

- [ ] **TRD-037**: Backend deployment to Railway (4h) - Priority: High - Depends: TRD-020, TRD-033
  - Create Railway project and configure Python service
  - Set environment variables (OPENAI_API_KEY, CORS_ORIGINS)
  - Configure build and start commands
  - Deploy and verify health check endpoint
  - Test `/api/parse` with production URL

- [ ] **TRD-038**: Frontend deployment to Vercel (3h) - Priority: High - Depends: TRD-029, TRD-037
  - Create Vercel project linked to GitHub repo
  - Configure build settings (Vite framework)
  - Set environment variables (VITE_API_BASE_URL = Railway URL)
  - Deploy and verify production build
  - Test complete workflow end-to-end on production URLs
  - Update CORS_ORIGINS on backend to include Vercel URL

---

## 12) Sprint Planning

### Sprint 1: Foundation & Setup (Days 1-2)

**Duration**: 2 days | **Total Estimate**: 16 hours | **Tasks**: TRD-001 to TRD-006

**Primary Tasks**:
- [ ] **TRD-001**: Project setup and repository initialization (2h)
- [ ] **TRD-002**: Backend environment setup (3h)
- [ ] **TRD-003**: Frontend environment setup (2h)
- [ ] **TRD-004**: Testing framework setup (3h)
- [ ] **TRD-005**: Logging and monitoring setup (2h)
- [ ] **TRD-006**: Test dataset creation (4h)

**Sprint Goals**:
- Complete development environment setup for backend and frontend
- Establish testing infrastructure
- Prepare test dataset for validation

**Definition of Done**:
- [ ] Backend and frontend run locally with no errors
- [ ] pytest and Jest execute successfully (even with no tests)
- [ ] Test dataset created with 10-20 samples and ground truth
- [ ] README.md documents setup steps

---

### Sprint 2: Backend Core (Days 3-5)

**Duration**: 3 days | **Total Estimate**: 24 hours | **Tasks**: TRD-007 to TRD-014

**Primary Tasks**:
- [ ] **TRD-007**: FastAPI application structure (2h)
- [ ] **TRD-008**: Pydantic data models (3h)
- [ ] **TRD-009**: File validation service (4h)
- [ ] **TRD-010**: Retry logic utility (2h)
- [ ] **TRD-011**: GPT-4o integration service (6h)
- [ ] **TRD-012**: Confidence scoring service (4h)
- [ ] **TRD-013**: Parse endpoint implementation (4h)
- [ ] **TRD-014**: Error handling implementation (3h)

**Sprint Goals**:
- Complete backend API implementation
- Integrate GPT-4o for invoice parsing
- Implement confidence scoring and error handling

**Definition of Done**:
- [ ] `/api/parse` endpoint functional and returns structured JSON
- [ ] File validation rejects invalid files correctly
- [ ] GPT-4o integration works with retry logic
- [ ] Confidence scoring rejects low-confidence extractions
- [ ] All error scenarios return proper HTTP status codes and messages

---

### Sprint 3: Frontend Core (Days 6-7)

**Duration**: 2 days | **Total Estimate**: 16 hours | **Tasks**: TRD-021 to TRD-029

**Primary Tasks**:
- [ ] **TRD-021**: React application structure (2h)
- [ ] **TRD-022**: FileUpload component (3h)
- [ ] **TRD-023**: LoadingSpinner component (1h)
- [ ] **TRD-024**: ErrorDisplay component (2h)
- [ ] **TRD-025**: FormattedView component (4h)
- [ ] **TRD-026**: RawView component (2h)
- [ ] **TRD-027**: InvoiceDisplay component (3h)
- [ ] **TRD-028**: API client service (2h)
- [ ] **TRD-029**: Frontend integration and state management (3h)

**Sprint Goals**:
- Complete React UI implementation
- Integrate frontend with backend API
- Implement invoice display views (formatted + raw JSON)

**Definition of Done**:
- [ ] User can upload invoice via drag-drop or click
- [ ] Loading spinner displays during processing
- [ ] Formatted invoice view displays correctly
- [ ] Raw JSON view shows complete response data
- [ ] Copy to clipboard works
- [ ] Errors display with meaningful messages

---

### Sprint 4: Testing & Quality (Days 8-9)

**Duration**: 2 days | **Total Estimate**: 16 hours | **Tasks**: TRD-015, TRD-016, TRD-017, TRD-020, TRD-019, TRD-030, TRD-031, TRD-032, TRD-033, TRD-034, TRD-035, TRD-036

**Primary Tasks**:
- [ ] **TRD-015**: Backend unit tests (5h)
- [ ] **TRD-016**: Backend integration tests (4h)
- [ ] **TRD-017**: Performance optimization (3h)
- [ ] **TRD-018**: Backend API documentation (2h)
- [ ] **TRD-019**: Security hardening (3h)
- [ ] **TRD-020**: Backend configuration management (2h)
- [ ] **TRD-030**: Frontend unit tests (4h)
- [ ] **TRD-031**: Frontend integration tests (3h)
- [ ] **TRD-032**: E2E tests with Playwright (5h)
- [ ] **TRD-033**: Accuracy validation against test dataset (4h)
- [ ] **TRD-034**: Performance testing (3h)
- [ ] **TRD-035**: Code coverage analysis (2h)
- [ ] **TRD-036**: Security testing (3h)

**Sprint Goals**:
- Achieve ≥80% backend unit test coverage
- Validate ≥90% field extraction accuracy on test dataset
- Verify ≤20s parse time performance
- Complete E2E testing with Playwright
- Security review and hardening

**Definition of Done**:
- [ ] All unit tests passing with ≥80% coverage
- [ ] Integration tests validate end-to-end API flow
- [ ] E2E tests validate complete user workflow
- [ ] Accuracy ≥90% on test dataset
- [ ] Parse time ≤20s for all test samples
- [ ] Security testing passes (no critical vulnerabilities)

---

### Sprint 5: Deployment & Demo Prep (Days 10)

**Duration**: 1 day | **Total Estimate**: 7 hours | **Tasks**: TRD-037, TRD-038

**Primary Tasks**:
- [ ] **TRD-037**: Backend deployment to Railway (4h)
- [ ] **TRD-038**: Frontend deployment to Vercel (3h)

**Sprint Goals**:
- Deploy backend to Railway with environment variables
- Deploy frontend to Vercel with API URL configuration
- Validate production deployment end-to-end

**Definition of Done (v1 Launch)**:
- [ ] Backend API successfully parses clean PDF invoices with 90%+ accuracy
- [ ] Frontend displays formatted invoice view with table-based layout
- [ ] JSON toggle displays formatted/pretty-printed raw data with confidence scores
- [ ] Copy to clipboard functionality works reliably
- [ ] Error handling displays meaningful messages in UI error area
- [ ] Deployed to Vercel (frontend) and Railway (backend)
- [ ] Successfully demos with test dataset (10-20 invoices)

---

## 13) Quality Gates & Definition of Done

### 13.1) Per-Task Quality Gates

**All Tasks Must Meet**:
- [ ] Code follows project style guide (PEP 8 for Python, ESLint for JavaScript)
- [ ] No critical linter warnings or errors
- [ ] All new code has associated tests
- [ ] Tests pass locally before commit
- [ ] Documentation updated (inline comments, README if needed)

### 13.2) Backend Quality Gates

- [ ] All Pydantic models validated with example data
- [ ] File validation tested with edge cases (boundary sizes, spoofed MIME types)
- [ ] GPT-4o integration tested with mocked responses
- [ ] Confidence scoring logic tested with synthetic data (0%, 50%, 90%, 100%)
- [ ] Error responses match specified format
- [ ] No invoice content in logs (metadata only)
- [ ] CORS configured correctly for frontend origin
- [ ] OpenAPI docs accessible at `/docs`

### 13.3) Frontend Quality Gates

- [ ] All components render without errors
- [ ] File upload accepts only valid file types (client-side check)
- [ ] Loading states display correctly during API calls
- [ ] Error messages user-friendly and actionable
- [ ] JSON display formatted and readable
- [ ] Copy to clipboard tested on Chrome and Edge
- [ ] Responsive design works on desktop (1920x1080 and 1366x768)

### 13.4) Integration Quality Gates

- [ ] Backend + Frontend integration tested locally
- [ ] Network errors handled gracefully
- [ ] Timeout scenarios tested (>20s mock delay)
- [ ] CORS preflight requests succeed
- [ ] E2E workflow tested with real invoice samples

### 13.5) Overall Project Definition of Done

**Must-Have Criteria**:
- [ ] Backend API successfully parses clean PDF invoices with 90%+ accuracy (validated against test dataset)
- [ ] Frontend displays formatted invoice view with table-based layout
- [ ] JSON toggle displays formatted/pretty-printed raw data with confidence scores
- [ ] Copy to clipboard functionality works reliably
- [ ] Error handling displays meaningful messages in UI error area
- [ ] Deployed to Vercel (frontend) and Railway (backend)
- [ ] Successfully demos with test dataset (10-20 invoices)

**Testing Coverage**:
- [ ] Backend unit tests: ≥80% coverage
- [ ] Frontend unit tests: ≥70% coverage
- [ ] Integration tests: All critical paths covered
- [ ] E2E tests: Complete user workflow validated
- [ ] Performance tests: All samples ≤20s parse time

**Non-Functional Requirements**:
- [ ] NFR-001: Parse time ≤20s for files ≤5MB (validated)
- [ ] NFR-002: 99% uptime (aspirational, basic logging in place)
- [ ] NFR-003: Input validation implemented and tested
- [ ] NFR-004: No data persistence (code review confirmed)
- [ ] NFR-005: Processing time included in response metadata

---

## 14) Risk Mitigation & Contingency Plans

### 14.1) Technical Risks

**RISK-001: GPT-4o Accuracy Below 90% Target**

- **Likelihood**: Medium
- **Impact**: High (blocks demo success criteria)
- **Mitigation**:
  - Refine prompt engineering with explicit field extraction instructions
  - Add few-shot examples in prompt for edge cases
  - Test with diverse invoice layouts during development
  - Implement field-level confidence scoring to identify weak extractions
- **Contingency**: If accuracy <90%, focus on high-confidence subset and document limitations

**RISK-002: GPT-4o API Latency Exceeds 20s**

- **Likelihood**: Low
- **Impact**: Medium (blocks NFR-001)
- **Mitigation**:
  - Optimize image encoding/compression before sending to API
  - Use latest GPT-4o model (typically faster)
  - Monitor p95/p99 latency during testing
- **Contingency**: Increase timeout to 25s if majority of samples <20s but outliers exceed

**RISK-003: PDF to Image Conversion Performance Issues**

- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**:
  - Use PyMuPDF (fastest library for PDF rendering)
  - Convert only first page (invoices typically single-page or first page sufficient)
  - Optimize image resolution (balance quality vs size)
- **Contingency**: For multi-page PDFs, extract text directly instead of using Vision API

**RISK-004: CORS or Cross-Origin Issues in Production**

- **Likelihood**: Medium
- **Impact**: High (blocks frontend-backend communication)
- **Mitigation**:
  - Test CORS configuration locally with different origins
  - Configure Railway and Vercel URLs correctly before deployment
  - Add both preview and production Vercel URLs to CORS whitelist
- **Contingency**: Use proxy configuration in Vercel if CORS issues persist

### 14.2) Schedule Risks

**RISK-005: GPT-4o Integration Takes Longer Than Estimated**

- **Likelihood**: Medium
- **Impact**: Medium (delays Sprint 2)
- **Mitigation**:
  - Start GPT-4o integration early in Sprint 2
  - Allocate buffer time (6h estimate includes learning curve)
  - Use OpenAI SDK examples and documentation
- **Contingency**: Defer optional features (line item limit to 20 instead of 50, skip Spanish language support) to stay on schedule

**RISK-006: Test Dataset Creation Delayed**

- **Likelihood**: Low
- **Impact**: High (blocks accuracy validation)
- **Mitigation**:
  - Parallelize dataset creation with Sprint 1
  - Use publicly available invoice templates/examples
  - Manually verify ground truth fields
- **Contingency**: Start with 5-10 samples for initial testing, add more during Sprint 4

### 14.3) Quality Risks

**RISK-007: Unit Test Coverage Below 80%**

- **Likelihood**: Low
- **Impact**: Medium (fails quality gate)
- **Mitigation**:
  - Write tests alongside implementation (test-driven development)
  - Use pytest-cov to track coverage during development
  - Identify uncovered code paths and add tests in Sprint 4
- **Contingency**: Prioritize testing critical paths (file validation, confidence scoring, parse endpoint) even if overall coverage <80%

---

## 15) Appendices

### 15.1) Glossary

- **Clean PDF**: High-quality PDF with typed text (not scanned/handwritten)
- **Confidence Score**: 0.0-1.0 value indicating AI's certainty in extracted field
- **Critical Field**: Field that must be ≥50% confidence or parsing is rejected
- **Field-Level Confidence**: Individual confidence score for each extracted field
- **Ground Truth**: Manually verified correct values for test dataset validation
- **Overall Confidence**: Minimum confidence score across all critical fields
- **Stateless**: No data persistence between requests (in-memory processing only)

### 15.2) References

- **PRD**: [PRD-20251020-INVOICE-PARSER v1.1](/home/james/dev/invoice-parser/docs/PRD/PRD-20251020-invoice-parser.md)
- **OpenAI GPT-4o Documentation**: https://platform.openai.com/docs/guides/vision
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Playwright Documentation**: https://playwright.dev/

### 15.3) Environment Setup Checklists

**Backend Setup**:
```bash
# 1. Clone repository
git clone <repo-url>
cd invoice-parser/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add:
#   OPENAI_API_KEY=sk-...
#   CORS_ORIGINS=http://localhost:5173

# 5. Run tests
pytest

# 6. Start development server
uvicorn main:app --reload
```

**Frontend Setup**:
```bash
# 1. Navigate to frontend
cd invoice-parser/frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env.local
# Edit .env.local and add:
#   VITE_API_BASE_URL=http://localhost:8000

# 4. Run tests
npm test

# 5. Start development server
npm run dev
```

---

## 16) Changelog

| Version | Date       | Change                                      | Author        |
| ------- | ---------- | ------------------------------------------- | ------------- |
| 1.0     | 2025-10-20 | Initial TRD created from PRD v1.1           | TBD           |

---

**Ready for Implementation** ✅

This TRD provides comprehensive technical specifications, task breakdown, and implementation guidance for the Invoice Parser project. All tasks are estimated, prioritized, and organized into 5 sprints totaling approximately 2 weeks of development time.

**Next Steps**:
1. Review and approve TRD with stakeholders
2. Assign technical lead and engineering team
3. Begin Sprint 1 (Foundation & Setup)
4. Use `/implement-trd` command to track task progress
