"""
Test Suite for GPT-4o Integration Service (TDD RED Phase)

Tests the invoice parsing service that integrates with OpenAI's GPT-4o API
for semantic extraction and OCR capabilities. These tests are designed to FAIL
during the RED phase of TDD since the service implementation does not yet exist.

Test Coverage:
- PDF invoice parsing
- Image invoice parsing (JPEG/PNG)
- Text invoice parsing
- Confidence score validation
- Retry mechanism behavior
- Timeout handling
- Response schema validation
- Malformed response handling
- Critical field extraction
- Missing optional field handling
- GPT-4o configuration validation
- Metadata inclusion

TRD References:
- Section 6: GPT-4o Integration Architecture
- Section 6.1: Prompt Engineering Strategy
- Section 6.2: Error Handling & Retry Logic
- NFR-001: Parse time ≤20s
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import json
import asyncio

# These imports will FAIL in RED phase - this is expected behavior
from app.services.gpt4o_service import GPT4oService, InvoiceParsingError
from app.schemas import (
    InvoiceResponse,
    FieldValue,
    SupplierInfo,
    CustomerInfo,
    InvoiceSummary,
    LineItem,
    InvoiceMetadata,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_openai_client():
    """
    Create mock AsyncOpenAI client for testing without real API calls.

    Returns mock client with chat.completions.create method that can be
    configured to return realistic GPT-4o responses.
    """
    client = AsyncMock()
    client.chat = AsyncMock()
    client.chat.completions = AsyncMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def sample_pdf_content():
    """
    Mock PDF file content for testing.

    In production, this would be actual PDF bytes. For testing, we mock
    the file reading behavior and focus on GPT-4o response handling.
    """
    return b"%PDF-1.4 mock pdf content with invoice data..."


@pytest.fixture
def sample_image_content():
    """
    Mock JPEG image file content for testing.

    Simulates an invoice scan or photo that would be processed by GPT-4o Vision.
    """
    return b"\xff\xd8\xff\xe0mock jpeg invoice image content..."


@pytest.fixture
def sample_text_content():
    """
    Mock plain text invoice content for testing.

    Simulates a simple text-based invoice that GPT-4o can parse directly.
    """
    return "INVOICE\nACME Corporation\n123 Main St\nInvoice #: INV-001\nDate: 2024-01-15..."


@pytest.fixture
def mock_gpt4o_response():
    """
    Create realistic mock GPT-4o API response with valid invoice data.

    This fixture returns the exact structure expected from OpenAI's API,
    including the nested response format and JSON content extraction.
    """
    # Ground truth invoice data matching InvoiceResponse schema
    invoice_data = {
        "supplier": {
            "name": {"value": "ACME Corporation", "confidence": 0.98},
            "address": {"value": "123 Main Street, New York, NY 10001", "confidence": 0.95},
            "phone": {"value": "+1-555-123-4567", "confidence": 0.92},
            "email": {"value": "billing@acme.com", "confidence": 0.94},
            "tax_id": {"value": "12-3456789", "confidence": 0.96},
        },
        "customer": {
            "name": {"value": "TechStart Inc", "confidence": 0.97},
            "address": {"value": "456 Oak Avenue, San Francisco, CA 94102", "confidence": 0.93},
            "account_id": {"value": "CUST-9876", "confidence": 0.91},
        },
        "invoice": {
            "number": {"value": "INV-2024-001", "confidence": 0.99},
            "issue_date": {"value": "2024-01-15", "confidence": 0.98},
            "due_date": {"value": "2024-02-15", "confidence": 0.97},
            "currency": {"value": "USD", "confidence": 1.0},
            "subtotal": {"value": 1150.00, "confidence": 0.95},
            "tax_amount": {"value": 100.00, "confidence": 0.94},
            "total_amount": {"value": 1250.00, "confidence": 0.96},
            "payment_terms": {"value": "Net 30", "confidence": 0.89},
        },
        "line_items": [
            {
                "sku": {"value": "PROD-123", "confidence": 0.92},
                "description": {"value": "Professional Services - Consulting", "confidence": 0.98},
                "quantity": {"value": 10, "confidence": 0.95},
                "unit_price": {"value": 100.00, "confidence": 0.96},
                "total": {"value": 1000.00, "confidence": 0.97},
            },
            {
                "description": {"value": "Software License - Annual", "confidence": 0.97},
                "quantity": {"value": 1, "confidence": 0.99},
                "unit_price": {"value": 150.00, "confidence": 0.98},
                "total": {"value": 150.00, "confidence": 0.98},
            },
        ],
    }

    # Mock OpenAI response structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps(invoice_data)
    mock_response.model = "gpt-4o-2024-08-06"
    mock_response.usage = MagicMock()
    mock_response.usage.total_tokens = 1250

    return mock_response


@pytest.fixture
def mock_malformed_gpt4o_response():
    """
    Create mock GPT-4o response with invalid/malformed JSON.

    Tests service's ability to handle GPT-4o returning non-parseable content
    or content that doesn't match the expected schema.
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    # Malformed JSON missing required fields
    mock_response.choices[0].message.content = '{"invalid": "structure", "missing": "required_fields"'
    mock_response.model = "gpt-4o-2024-08-06"

    return mock_response


@pytest.fixture
def gpt4o_service(mock_openai_client):
    """
    Create GPT4oService instance with mocked OpenAI client.

    Service should initialize with API client and configuration parameters
    per TRD Section 6.
    """
    # This will FAIL in RED phase - service doesn't exist yet
    return GPT4oService(
        openai_client=mock_openai_client,
        model="gpt-4o",
        temperature=0.4,
        max_tokens=4096,
        timeout=20.0,
    )


# ============================================================================
# Test Cases - Core Parsing Functionality
# ============================================================================


@pytest.mark.asyncio
async def test_parses_pdf_invoice_successfully(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_gpt4o_response
):
    """
    Test GPT-4o successfully parses PDF invoice into InvoiceResponse.

    Validates:
    - PDF file is processed correctly
    - GPT-4o API called with correct parameters
    - Response deserialized into valid InvoiceResponse schema
    - All critical fields extracted

    TRD Reference: Section 6 - PDF format support
    """
    # Configure mock to return valid invoice response
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="invoice.pdf",
        mime_type="application/pdf",
    )

    # Assertions
    assert isinstance(result, InvoiceResponse), "Service should return InvoiceResponse instance"
    assert result.supplier.name.value == "ACME Corporation"
    assert result.customer.name.value == "TechStart Inc"
    assert result.invoice.number.value == "INV-2024-001"
    assert result.invoice.total_amount.value == 1250.00
    assert len(result.line_items) == 2
    assert result.meta.source_file_name == "invoice.pdf"
    assert result.meta.source_format == "pdf"

    # Verify OpenAI client called correctly
    mock_openai_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4o"
    assert call_kwargs["temperature"] == 0.4
    assert call_kwargs["max_tokens"] == 4096


@pytest.mark.asyncio
async def test_parses_image_invoice_successfully(
    gpt4o_service, mock_openai_client, sample_image_content, mock_gpt4o_response
):
    """
    Test GPT-4o successfully parses image invoice (JPEG/PNG) using Vision API.

    Validates:
    - Image file processed via GPT-4o Vision capabilities
    - OCR extraction works on scanned invoices
    - Response matches InvoiceResponse schema

    TRD Reference: Section 6 - Image format support with OCR
    """
    # Configure mock to return valid invoice response
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing with JPEG image
    result = await gpt4o_service.parse_invoice(
        file_content=sample_image_content,
        file_name="invoice_scan.jpg",
        mime_type="image/jpeg",
    )

    # Assertions
    assert isinstance(result, InvoiceResponse)
    assert result.meta.source_file_name == "invoice_scan.jpg"
    assert result.meta.source_format == "image"
    assert result.supplier.name.value == "ACME Corporation"

    # Verify Vision API called (should include image in messages)
    mock_openai_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_parses_text_invoice_successfully(
    gpt4o_service, mock_openai_client, sample_text_content, mock_gpt4o_response
):
    """
    Test GPT-4o successfully parses plain text invoice.

    Validates:
    - Text files processed directly without OCR
    - Semantic extraction works on unstructured text
    - Response matches InvoiceResponse schema

    TRD Reference: Section 6 - Text format support
    """
    # Configure mock to return valid invoice response
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing with plain text
    result = await gpt4o_service.parse_invoice(
        file_content=sample_text_content.encode("utf-8"),
        file_name="invoice.txt",
        mime_type="text/plain",
    )

    # Assertions
    assert isinstance(result, InvoiceResponse)
    assert result.meta.source_file_name == "invoice.txt"
    assert result.meta.source_format == "text"
    assert result.invoice.number.value == "INV-2024-001"


# ============================================================================
# Test Cases - Confidence Scoring
# ============================================================================


@pytest.mark.asyncio
async def test_returns_confidence_scores(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_gpt4o_response
):
    """
    Test that all extracted fields include confidence scores.

    Validates:
    - Every FieldValue has confidence in range [0.0, 1.0]
    - Confidence scores are extracted from GPT-4o response
    - Overall confidence calculated in metadata

    TRD Reference: Section 6.1 - Confidence scoring requirement
    """
    # Configure mock
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="invoice.pdf",
        mime_type="application/pdf",
    )

    # Validate confidence scores on supplier fields
    assert 0.0 <= result.supplier.name.confidence <= 1.0
    assert 0.0 <= result.supplier.address.confidence <= 1.0
    assert 0.0 <= result.supplier.tax_id.confidence <= 1.0

    # Validate confidence scores on customer fields
    assert 0.0 <= result.customer.name.confidence <= 1.0

    # Validate confidence scores on invoice fields
    assert 0.0 <= result.invoice.number.confidence <= 1.0
    assert 0.0 <= result.invoice.total_amount.confidence <= 1.0

    # Validate confidence scores on line items
    for line_item in result.line_items:
        assert 0.0 <= line_item.description.confidence <= 1.0
        if line_item.quantity:
            assert 0.0 <= line_item.quantity.confidence <= 1.0

    # Validate overall confidence in metadata
    assert result.meta.overall_confidence is not None
    assert 0.0 <= result.meta.overall_confidence <= 1.0


# ============================================================================
# Test Cases - Error Handling & Retry Logic
# ============================================================================


@pytest.mark.asyncio
async def test_retries_on_openai_error(gpt4o_service, mock_openai_client, sample_pdf_content):
    """
    Test service retries on transient OpenAI API errors using exponential backoff.

    Validates:
    - Retry utility invoked on RateLimitError
    - Exponential backoff strategy applied
    - Eventually succeeds after retries

    TRD Reference: Section 6.2 - Retry mechanism with exponential backoff
    """
    from openai import RateLimitError

    # Configure mock to fail twice then succeed
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "supplier": {"name": {"value": "Test Corp", "confidence": 0.9}},
        "customer": {"name": {"value": "Client Inc", "confidence": 0.9}},
        "invoice": {
            "number": {"value": "INV-001", "confidence": 0.9},
            "issue_date": {"value": "2024-01-15", "confidence": 0.9},
            "due_date": {"value": "2024-02-15", "confidence": 0.9},
        },
    })

    # Simulate: fail with rate limit, fail again, then succeed
    mock_openai_client.chat.completions.create.side_effect = [
        RateLimitError("Rate limit exceeded", response=MagicMock(), body=None),
        RateLimitError("Rate limit exceeded", response=MagicMock(), body=None),
        mock_response,
    ]

    # Execute - should succeed after 2 retries
    with patch("app.services.gpt4o_service.retry_with_exponential_backoff") as mock_retry:
        # Configure retry utility to pass through to actual API call
        mock_retry.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)

        result = await gpt4o_service.parse_invoice(
            file_content=sample_pdf_content,
            file_name="invoice.pdf",
            mime_type="application/pdf",
        )

    # Verify retry utility was used
    assert mock_retry.called, "Retry utility should be invoked"


@pytest.mark.asyncio
async def test_respects_timeout(gpt4o_service, mock_openai_client, sample_pdf_content):
    """
    Test service raises error if GPT-4o request exceeds timeout.

    Validates:
    - Timeout configured correctly (20s per TRD)
    - APITimeoutError raised when timeout exceeded
    - Request cancelled appropriately

    TRD Reference: NFR-001 - Parse time ≤20s
    """
    from openai import APITimeoutError

    # Configure mock to raise timeout error
    mock_openai_client.chat.completions.create.side_effect = APITimeoutError(
        "Request timed out after 20 seconds"
    )

    # Execute and expect timeout error
    with pytest.raises((APITimeoutError, InvoiceParsingError)):
        await gpt4o_service.parse_invoice(
            file_content=sample_pdf_content,
            file_name="invoice.pdf",
            mime_type="application/pdf",
        )


# ============================================================================
# Test Cases - Schema Validation
# ============================================================================


@pytest.mark.asyncio
async def test_validates_response_schema(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_gpt4o_response
):
    """
    Test service validates GPT-4o response against InvoiceResponse schema.

    Validates:
    - Response deserialized using Pydantic models
    - Schema validation catches invalid data
    - All required fields present

    TRD Reference: Section 5.1 - Schema enforcement
    """
    # Configure mock
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="invoice.pdf",
        mime_type="application/pdf",
    )

    # Validate schema compliance
    assert isinstance(result, InvoiceResponse)
    assert isinstance(result.supplier, SupplierInfo)
    assert isinstance(result.customer, CustomerInfo)
    assert isinstance(result.invoice, InvoiceSummary)
    assert isinstance(result.meta, InvoiceMetadata)
    assert all(isinstance(item, LineItem) for item in result.line_items)

    # Validate required fields
    assert result.supplier.name is not None
    assert result.customer.name is not None
    assert result.invoice.number is not None
    assert result.invoice.issue_date is not None
    assert result.invoice.due_date is not None


@pytest.mark.asyncio
async def test_handles_malformed_response(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_malformed_gpt4o_response
):
    """
    Test service handles GPT-4o returning invalid/malformed JSON.

    Validates:
    - Malformed JSON caught and handled gracefully
    - Appropriate error raised (InvoiceParsingError)
    - Error message provides useful debugging info

    TRD Reference: Section 6.2 - Error handling
    """
    # Configure mock to return malformed response
    mock_openai_client.chat.completions.create.return_value = mock_malformed_gpt4o_response

    # Execute and expect parsing error
    with pytest.raises(InvoiceParsingError) as exc_info:
        await gpt4o_service.parse_invoice(
            file_content=sample_pdf_content,
            file_name="invoice.pdf",
            mime_type="application/pdf",
        )

    # Verify error message is informative
    assert "malformed" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


# ============================================================================
# Test Cases - Field Extraction Completeness
# ============================================================================


@pytest.mark.asyncio
async def test_extracts_all_critical_fields(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_gpt4o_response
):
    """
    Test service extracts all critical invoice fields.

    Critical fields per TRD Section 6.1:
    - Supplier: name, address, tax_id
    - Customer: name
    - Invoice: number, issue_date, due_date, total_amount
    - Line items: description, quantity, unit_price, total

    TRD Reference: Section 6.1 - Field extraction requirements
    """
    # Configure mock
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="invoice.pdf",
        mime_type="application/pdf",
    )

    # Supplier critical fields
    assert result.supplier.name.value == "ACME Corporation"
    assert result.supplier.address.value == "123 Main Street, New York, NY 10001"
    assert result.supplier.tax_id.value == "12-3456789"

    # Customer critical fields
    assert result.customer.name.value == "TechStart Inc"

    # Invoice critical fields
    assert result.invoice.number.value == "INV-2024-001"
    assert result.invoice.issue_date.value == "2024-01-15"
    assert result.invoice.due_date.value == "2024-02-15"
    assert result.invoice.total_amount.value == 1250.00

    # Line item critical fields
    assert len(result.line_items) >= 1
    first_item = result.line_items[0]
    assert first_item.description.value == "Professional Services - Consulting"
    assert first_item.quantity.value == 10
    assert first_item.unit_price.value == 100.00
    assert first_item.total.value == 1000.00


@pytest.mark.asyncio
async def test_handles_missing_optional_fields(
    gpt4o_service, mock_openai_client, sample_pdf_content
):
    """
    Test service gracefully handles missing optional fields.

    Validates:
    - Optional fields (email, phone, PO number) can be None
    - Service doesn't fail when optional data missing
    - Schema validation still passes

    TRD Reference: Section 5.1 - Optional field handling
    """
    # Create mock response with minimal required fields only
    minimal_invoice_data = {
        "supplier": {
            "name": {"value": "Minimal Corp", "confidence": 0.9},
            # Missing: address, phone, email, tax_id
        },
        "customer": {
            "name": {"value": "Customer Inc", "confidence": 0.9},
            # Missing: address, account_id
        },
        "invoice": {
            "number": {"value": "INV-MIN-001", "confidence": 0.9},
            "issue_date": {"value": "2024-01-15", "confidence": 0.9},
            "due_date": {"value": "2024-02-15", "confidence": 0.9},
            # Missing: currency, subtotal, tax, total, payment_terms, po_number
        },
        "line_items": [],
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps(minimal_invoice_data)
    mock_response.model = "gpt-4o-2024-08-06"

    mock_openai_client.chat.completions.create.return_value = mock_response

    # Execute parsing
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="minimal_invoice.pdf",
        mime_type="application/pdf",
    )

    # Validate required fields present
    assert result.supplier.name.value == "Minimal Corp"
    assert result.customer.name.value == "Customer Inc"
    assert result.invoice.number.value == "INV-MIN-001"

    # Validate optional fields are None
    assert result.supplier.email is None
    assert result.supplier.phone is None
    assert result.customer.account_id is None
    assert result.invoice.payment_terms is None
    assert result.invoice.po_number is None


# ============================================================================
# Test Cases - Configuration Validation
# ============================================================================


@pytest.mark.asyncio
async def test_uses_correct_model_and_temperature(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_gpt4o_response
):
    """
    Test service uses correct GPT-4o model and temperature settings.

    Validates:
    - Model: "gpt-4o" (per TRD Section 6)
    - Temperature: 0.4 (balanced between creativity and consistency)
    - Max tokens: 4096 (sufficient for complex invoices)

    TRD Reference: Section 6 - GPT-4o configuration
    """
    # Configure mock
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing
    await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="invoice.pdf",
        mime_type="application/pdf",
    )

    # Verify API call parameters
    call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4o", "Should use gpt-4o model"
    assert call_kwargs["temperature"] == 0.4, "Should use temperature 0.4"
    assert call_kwargs["max_tokens"] == 4096, "Should use max_tokens 4096"


@pytest.mark.asyncio
async def test_includes_metadata_in_response(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_gpt4o_response
):
    """
    Test service includes metadata in response.

    Metadata should include:
    - source_file_name
    - source_format (pdf/image/text)
    - model_version
    - processing_time_seconds
    - overall_confidence

    TRD Reference: Section 5.1 - Metadata requirements
    """
    # Configure mock
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute parsing
    start_time = datetime.now()
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="test_invoice.pdf",
        mime_type="application/pdf",
    )
    end_time = datetime.now()

    # Validate metadata fields
    assert result.meta.source_file_name == "test_invoice.pdf"
    assert result.meta.source_format == "pdf"
    assert result.meta.model_version == "gpt-4o-2024-08-06"

    # Validate processing time recorded
    assert result.meta.processing_time_seconds is not None
    assert result.meta.processing_time_seconds >= 0
    # Should be less than total test execution time
    assert result.meta.processing_time_seconds <= (end_time - start_time).total_seconds()

    # Validate overall confidence calculated
    assert result.meta.overall_confidence is not None
    assert 0.0 <= result.meta.overall_confidence <= 1.0


# ============================================================================
# Additional Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_handles_empty_line_items(
    gpt4o_service, mock_openai_client, sample_pdf_content
):
    """
    Test service handles invoices with no line items (summary invoices).

    Some invoices only have total amounts without itemized breakdowns.
    Service should handle this gracefully.
    """
    # Create response with no line items
    invoice_data = {
        "supplier": {"name": {"value": "Corp Inc", "confidence": 0.9}},
        "customer": {"name": {"value": "Client LLC", "confidence": 0.9}},
        "invoice": {
            "number": {"value": "INV-SUMMARY-001", "confidence": 0.9},
            "issue_date": {"value": "2024-01-15", "confidence": 0.9},
            "due_date": {"value": "2024-02-15", "confidence": 0.9},
            "total_amount": {"value": 5000.00, "confidence": 0.9},
        },
        "line_items": [],
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps(invoice_data)
    mock_response.model = "gpt-4o-2024-08-06"

    mock_openai_client.chat.completions.create.return_value = mock_response

    # Execute parsing
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="summary_invoice.pdf",
        mime_type="application/pdf",
    )

    # Validate
    assert isinstance(result, InvoiceResponse)
    assert len(result.line_items) == 0
    assert result.invoice.total_amount.value == 5000.00


@pytest.mark.asyncio
async def test_handles_max_line_items_limit(
    gpt4o_service, mock_openai_client, sample_pdf_content
):
    """
    Test service respects max line items limit (50 per schema).

    Validates:
    - Schema max_length=50 enforced
    - Service handles truncation or validation appropriately

    TRD Reference: Section 5.1 - Line items max 50
    """
    # Create response with exactly 50 line items (at limit)
    line_items = [
        {
            "description": {"value": f"Item {i}", "confidence": 0.9},
            "quantity": {"value": 1, "confidence": 0.9},
            "unit_price": {"value": 10.00, "confidence": 0.9},
            "total": {"value": 10.00, "confidence": 0.9},
        }
        for i in range(50)
    ]

    invoice_data = {
        "supplier": {"name": {"value": "Corp Inc", "confidence": 0.9}},
        "customer": {"name": {"value": "Client LLC", "confidence": 0.9}},
        "invoice": {
            "number": {"value": "INV-LARGE-001", "confidence": 0.9},
            "issue_date": {"value": "2024-01-15", "confidence": 0.9},
            "due_date": {"value": "2024-02-15", "confidence": 0.9},
            "total_amount": {"value": 500.00, "confidence": 0.9},
        },
        "line_items": line_items,
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps(invoice_data)
    mock_response.model = "gpt-4o-2024-08-06"

    mock_openai_client.chat.completions.create.return_value = mock_response

    # Execute parsing
    result = await gpt4o_service.parse_invoice(
        file_content=sample_pdf_content,
        file_name="large_invoice.pdf",
        mime_type="application/pdf",
    )

    # Validate
    assert isinstance(result, InvoiceResponse)
    assert len(result.line_items) == 50


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.asyncio
async def test_parsing_completes_within_timeout(
    gpt4o_service, mock_openai_client, sample_pdf_content, mock_gpt4o_response
):
    """
    Test parsing completes within required timeout (20s).

    While this is a unit test with mocks, it validates the service
    structure doesn't introduce unnecessary delays.

    TRD Reference: NFR-001 - Parse time ≤20s
    """
    # Configure mock
    mock_openai_client.chat.completions.create.return_value = mock_gpt4o_response

    # Execute with timeout
    start = datetime.now()
    result = await asyncio.wait_for(
        gpt4o_service.parse_invoice(
            file_content=sample_pdf_content,
            file_name="invoice.pdf",
            mime_type="application/pdf",
        ),
        timeout=20.0,
    )
    elapsed = (datetime.now() - start).total_seconds()

    # Validate completed successfully
    assert isinstance(result, InvoiceResponse)

    # In unit tests with mocks, should complete very quickly
    assert elapsed < 1.0, "Unit test should complete in <1s with mocks"
