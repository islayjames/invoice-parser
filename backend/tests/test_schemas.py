"""
Test suite for Pydantic schema models (TRD-007)

RED Phase: These tests are expected to FAIL because the schema models
have not been implemented yet. This is intentional in TDD.

Tests cover:
- FieldValue validation (confidence range, value types)
- SupplierInfo structure
- CustomerInfo structure
- InvoiceSummary validation
- LineItem validation
- InvoiceMetadata defaults
- InvoiceResponse complete structure
- ErrorResponse structure
"""

import pytest
from pydantic import ValidationError

# These imports will fail in RED phase - that's expected!
from app.schemas import (
    FieldValue,
    SupplierInfo,
    CustomerInfo,
    InvoiceSummary,
    LineItem,
    InvoiceMetadata,
    InvoiceResponse,
    ErrorResponse,
    ErrorDetail
)


class TestFieldValue:
    """Test FieldValue model validation."""

    def test_field_value_validates_confidence_range(self):
        """Confidence must be between 0.0 and 1.0."""
        # Valid confidence values
        valid_field = FieldValue(value="Test Value", confidence=0.5)
        assert valid_field.confidence == 0.5

        valid_field_min = FieldValue(value="Test", confidence=0.0)
        assert valid_field_min.confidence == 0.0

        valid_field_max = FieldValue(value="Test", confidence=1.0)
        assert valid_field_max.confidence == 1.0

        # Invalid confidence > 1.0
        with pytest.raises(ValidationError) as exc_info:
            FieldValue(value="Test", confidence=1.5)
        assert "confidence" in str(exc_info.value).lower()

        # Invalid confidence < 0.0
        with pytest.raises(ValidationError) as exc_info:
            FieldValue(value="Test", confidence=-0.5)
        assert "confidence" in str(exc_info.value).lower()

    def test_field_value_accepts_string_values(self):
        """FieldValue should accept string values."""
        field = FieldValue(value="Invoice Number 12345", confidence=0.95)
        assert field.value == "Invoice Number 12345"
        assert field.confidence == 0.95
        assert isinstance(field.value, str)

    def test_field_value_accepts_numeric_values(self):
        """FieldValue should accept int and float values."""
        # Integer value
        field_int = FieldValue(value=12345, confidence=0.9)
        assert field_int.value == 12345
        assert isinstance(field_int.value, int)

        # Float value
        field_float = FieldValue(value=1234.56, confidence=0.92)
        assert field_float.value == 1234.56
        assert isinstance(field_float.value, float)

    def test_field_value_requires_both_fields(self):
        """FieldValue requires both value and confidence."""
        with pytest.raises(ValidationError) as exc_info:
            FieldValue(value="Test")  # Missing confidence

        with pytest.raises(ValidationError) as exc_info:
            FieldValue(confidence=0.9)  # Missing value


class TestInvoiceSummary:
    """Test InvoiceSummary model validation."""

    def test_invoice_summary_validates_required_fields(self):
        """InvoiceSummary must have required fields: number, issue_date, due_date."""
        # Valid invoice summary
        valid_summary = InvoiceSummary(
            number=FieldValue(value="INV-001", confidence=0.95),
            issue_date=FieldValue(value="2025-01-15", confidence=0.90),
            due_date=FieldValue(value="2025-02-15", confidence=0.88)
        )
        assert valid_summary.number.value == "INV-001"
        assert valid_summary.issue_date.value == "2025-01-15"

        # Missing required field should fail
        with pytest.raises(ValidationError):
            InvoiceSummary(
                number=FieldValue(value="INV-001", confidence=0.95),
                # Missing issue_date
                due_date=FieldValue(value="2025-02-15", confidence=0.88)
            )

    def test_invoice_summary_optional_fields(self):
        """InvoiceSummary optional fields: total_amount, currency, tax_amount."""
        summary = InvoiceSummary(
            number=FieldValue(value="INV-001", confidence=0.95),
            issue_date=FieldValue(value="2025-01-15", confidence=0.90),
            due_date=FieldValue(value="2025-02-15", confidence=0.88),
            total_amount=FieldValue(value=5000.00, confidence=0.98),
            currency=FieldValue(value="USD", confidence=0.99),
            tax_amount=FieldValue(value=500.00, confidence=0.95)
        )
        assert summary.total_amount.value == 5000.00
        assert summary.currency.value == "USD"


class TestLineItem:
    """Test LineItem model validation."""

    def test_line_item_validation(self):
        """LineItem should validate structure with description, quantity, unit_price, total."""
        line_item = LineItem(
            description=FieldValue(value="Consulting Services", confidence=0.92),
            quantity=FieldValue(value=10, confidence=0.95),
            unit_price=FieldValue(value=100.00, confidence=0.96),
            total=FieldValue(value=1000.00, confidence=0.98)
        )

        assert line_item.description.value == "Consulting Services"
        assert line_item.quantity.value == 10
        assert line_item.unit_price.value == 100.00
        assert line_item.total.value == 1000.00

    def test_line_item_requires_description(self):
        """LineItem must have at minimum a description field."""
        # Should work with just description
        line_item = LineItem(
            description=FieldValue(value="Item description", confidence=0.9)
        )
        assert line_item.description.value == "Item description"


class TestInvoiceMetadata:
    """Test InvoiceMetadata model."""

    def test_invoice_metadata_defaults(self):
        """InvoiceMetadata should have default values for model_version."""
        metadata = InvoiceMetadata(
            source_file_name="invoice.pdf",
            parse_timestamp="2025-10-20T12:00:00Z",
            processing_time_seconds=5.2
        )

        assert metadata.source_file_name == "invoice.pdf"
        assert metadata.model_version == "gpt-4o-2024-08-06"  # Default from TRD
        assert metadata.processing_time_seconds == 5.2

    def test_invoice_metadata_custom_model_version(self):
        """InvoiceMetadata should allow custom model_version."""
        metadata = InvoiceMetadata(
            source_file_name="invoice.pdf",
            parse_timestamp="2025-10-20T12:00:00Z",
            processing_time_seconds=3.1,
            model_version="gpt-4o-custom"
        )
        assert metadata.model_version == "gpt-4o-custom"


class TestInvoiceResponse:
    """Test complete InvoiceResponse structure."""

    def test_invoice_response_full_schema(self):
        """InvoiceResponse should validate complete invoice structure."""
        invoice_response = InvoiceResponse(
            supplier=SupplierInfo(
                name=FieldValue(value="Acme Corp", confidence=0.95),
                address=FieldValue(value="123 Main St", confidence=0.90)
            ),
            customer=CustomerInfo(
                name=FieldValue(value="Client Inc", confidence=0.93),
                address=FieldValue(value="456 Oak Ave", confidence=0.88)
            ),
            invoice=InvoiceSummary(
                number=FieldValue(value="INV-001", confidence=0.96),
                issue_date=FieldValue(value="2025-01-15", confidence=0.92),
                due_date=FieldValue(value="2025-02-15", confidence=0.90)
            ),
            line_items=[
                LineItem(
                    description=FieldValue(value="Service 1", confidence=0.91),
                    quantity=FieldValue(value=2, confidence=0.95),
                    unit_price=FieldValue(value=500.00, confidence=0.94),
                    total=FieldValue(value=1000.00, confidence=0.96)
                )
            ],
            meta=InvoiceMetadata(
                source_file_name="invoice.pdf",
                parse_timestamp="2025-10-20T12:00:00Z",
                processing_time_seconds=4.5
            )
        )

        assert invoice_response.supplier.name.value == "Acme Corp"
        assert invoice_response.customer.name.value == "Client Inc"
        assert invoice_response.invoice.number.value == "INV-001"
        assert len(invoice_response.line_items) == 1
        assert invoice_response.meta.source_file_name == "invoice.pdf"

    def test_invoice_response_requires_all_main_sections(self):
        """InvoiceResponse requires supplier, customer, invoice, line_items, meta."""
        with pytest.raises(ValidationError):
            InvoiceResponse(
                # Missing supplier
                customer=CustomerInfo(
                    name=FieldValue(value="Client Inc", confidence=0.93)
                ),
                invoice=InvoiceSummary(
                    number=FieldValue(value="INV-001", confidence=0.96),
                    issue_date=FieldValue(value="2025-01-15", confidence=0.92),
                    due_date=FieldValue(value="2025-02-15", confidence=0.90)
                ),
                line_items=[],
                meta=InvoiceMetadata(
                    source_file_name="invoice.pdf",
                    parse_timestamp="2025-10-20T12:00:00Z",
                    processing_time_seconds=4.5
                )
            )


class TestErrorResponse:
    """Test ErrorResponse structure."""

    def test_error_response_structure(self):
        """ErrorResponse should contain error detail with code and message."""
        error_detail = ErrorDetail(
            code="INVALID_FILE_TYPE",
            message="File type application/exe is not supported. Allowed: PDF, PNG, JPEG, TXT.",
            details={"allowed_types": ["application/pdf", "image/png", "image/jpeg", "text/plain"]}
        )

        error_response = ErrorResponse(error=error_detail)

        assert error_response.error.code == "INVALID_FILE_TYPE"
        assert "not supported" in error_response.error.message
        assert "allowed_types" in error_response.error.details

    def test_error_response_requires_code_and_message(self):
        """ErrorDetail must have code and message fields."""
        with pytest.raises(ValidationError):
            ErrorDetail(code="ERROR_CODE")  # Missing message

        with pytest.raises(ValidationError):
            ErrorDetail(message="Error message")  # Missing code

    def test_error_response_optional_details(self):
        """ErrorDetail details field should be optional."""
        error_detail = ErrorDetail(
            code="PARSING_FAILED",
            message="Failed to extract invoice data."
        )
        error_response = ErrorResponse(error=error_detail)
        assert error_response.error.code == "PARSING_FAILED"
        assert error_response.error.details is None or error_response.error.details == {}
