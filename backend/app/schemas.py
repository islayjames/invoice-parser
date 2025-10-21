"""
Pydantic schema models for invoice parsing API (TRD Section 5.1)

Defines the data structures for invoice extraction responses and error handling.
All extracted fields include confidence scores to support downstream validation
and human review workflows.

Example:
    from app.schemas import InvoiceResponse, FieldValue

    response = InvoiceResponse(
        supplier=SupplierInfo(name=FieldValue(value="ACME Corp", confidence=0.95)),
        customer=CustomerInfo(name=FieldValue(value="Client Inc", confidence=0.90)),
        invoice=InvoiceSummary(
            number=FieldValue(value="INV-001", confidence=0.99),
            issue_date=FieldValue(value="2024-01-15", confidence=0.98),
            due_date=FieldValue(value="2024-02-15", confidence=0.97)
        ),
        line_items=[],
        meta=InvoiceMetadata(source_file_name="invoice.pdf")
    )
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime


class FieldValue(BaseModel):
    """
    Base model for extracted field values with confidence scoring.

    All extracted fields in the invoice are represented as FieldValue objects,
    which combine the actual extracted value with a confidence score from the
    GPT-4o model. This allows downstream systems to filter or flag low-confidence
    extractions for human review.

    Attributes:
        value: The extracted field value (string, number, or float)
        confidence: Model confidence score in range [0.0, 1.0] where 1.0 is highest confidence

    Example:
        invoice_number = FieldValue(value="INV-12345", confidence=0.95)
        total_amount = FieldValue(value=1250.00, confidence=0.99)
        uncertain_field = FieldValue(value="Unknown Inc", confidence=0.45)
    """
    value: str | float | int
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score [0.0-1.0]")


class SupplierInfo(BaseModel):
    """
    Information about the invoice supplier/vendor.

    Attributes:
        name: Supplier company or individual name (required)
        address: Physical or mailing address (optional)
        phone: Contact phone number (optional)
        email: Contact email address (optional)
        tax_id: Tax ID, VAT number, or EIN (optional)

    Example:
        supplier = SupplierInfo(
            name=FieldValue(value="ACME Corporation", confidence=0.98),
            address=FieldValue(value="123 Main St, City, ST 12345", confidence=0.92),
            tax_id=FieldValue(value="12-3456789", confidence=0.95)
        )
    """
    name: FieldValue = Field(..., description="Supplier company or individual name")
    address: Optional[FieldValue] = Field(None, description="Physical or mailing address")
    phone: Optional[FieldValue] = Field(None, description="Contact phone number")
    email: Optional[FieldValue] = Field(None, description="Contact email address")
    tax_id: Optional[FieldValue] = Field(None, description="Tax ID, VAT number, or EIN")


class CustomerInfo(BaseModel):
    """
    Information about the invoice customer/buyer.

    Attributes:
        name: Customer company or individual name (required)
        address: Billing or shipping address (optional)
        account_id: Customer account or reference number (optional)

    Example:
        customer = CustomerInfo(
            name=FieldValue(value="TechStart Inc", confidence=0.97),
            account_id=FieldValue(value="CUST-9876", confidence=0.94)
        )
    """
    name: FieldValue = Field(..., description="Customer company or individual name")
    address: Optional[FieldValue] = Field(None, description="Billing or shipping address")
    account_id: Optional[FieldValue] = Field(None, description="Customer account or reference number")


class InvoiceSummary(BaseModel):
    """
    Invoice header and summary information.

    Contains the core invoice metadata and financial totals. Supports multiple
    naming conventions for totals (total/total_amount, tax/tax_amount) to accommodate
    different invoice formats.

    Attributes:
        number: Invoice number or identifier (required)
        issue_date: Invoice issue/creation date (required)
        due_date: Payment due date (required)
        currency: Currency code (defaults to USD if not specified)
        subtotal: Pre-tax subtotal (optional)
        tax: Tax amount (optional, alias for tax_amount)
        total: Total amount including tax (optional, alias for total_amount)
        total_amount: Total amount including tax (optional)
        tax_amount: Tax amount (optional)
        payment_terms: Payment terms description (optional, e.g., "Net 30")
        po_number: Purchase order reference number (optional)

    Example:
        invoice = InvoiceSummary(
            number=FieldValue(value="INV-2024-001", confidence=0.99),
            issue_date=FieldValue(value="2024-01-15", confidence=0.98),
            due_date=FieldValue(value="2024-02-15", confidence=0.97),
            currency=FieldValue(value="USD", confidence=1.0),
            total_amount=FieldValue(value=1250.00, confidence=0.96)
        )
    """
    number: FieldValue = Field(..., description="Invoice number or identifier")
    issue_date: FieldValue = Field(..., description="Invoice issue/creation date")
    due_date: FieldValue = Field(..., description="Payment due date")
    currency: Optional[FieldValue] = Field(None, description="Currency code (defaults to USD)")
    subtotal: Optional[FieldValue] = Field(None, description="Pre-tax subtotal")
    tax: Optional[FieldValue] = Field(None, description="Tax amount (alias for tax_amount)")
    total: Optional[FieldValue] = Field(None, description="Total amount including tax (alias for total_amount)")
    total_amount: Optional[FieldValue] = Field(None, description="Total amount including tax")
    tax_amount: Optional[FieldValue] = Field(None, description="Tax amount")
    payment_terms: Optional[FieldValue] = Field(None, description="Payment terms (e.g., 'Net 30')")
    po_number: Optional[FieldValue] = Field(None, description="Purchase order reference number")

    @field_validator('currency')
    def default_currency(cls, v):
        """
        Apply default currency if not specified or empty.

        If the currency field is present but has an empty value, defaults to USD.
        This ensures consistent currency representation for downstream systems.

        Args:
            v: The currency FieldValue or None

        Returns:
            The currency FieldValue with USD default applied if needed, or None
        """
        if v is None:
            return None
        if v.value is None or v.value == "":
            v.value = "USD"
        return v


class LineItem(BaseModel):
    """
    Individual line item on the invoice.

    Represents a product or service line with pricing details. All fields except
    description are optional to accommodate varying invoice formats.

    Attributes:
        sku: Stock keeping unit or product code (optional)
        description: Item description or service name (required)
        quantity: Number of units (optional)
        unit_price: Price per unit (optional)
        discount: Discount amount or percentage (optional)
        tax_rate: Tax rate applied to this line (optional)
        total: Line item total amount (optional)

    Example:
        line_item = LineItem(
            sku=FieldValue(value="PROD-123", confidence=0.92),
            description=FieldValue(value="Professional Services - Consulting", confidence=0.98),
            quantity=FieldValue(value=10, confidence=0.95),
            unit_price=FieldValue(value=125.00, confidence=0.96),
            total=FieldValue(value=1250.00, confidence=0.97)
        )
    """
    sku: Optional[FieldValue] = Field(None, description="Stock keeping unit or product code")
    description: FieldValue = Field(..., description="Item description or service name")
    quantity: Optional[FieldValue] = Field(None, description="Number of units")
    unit_price: Optional[FieldValue] = Field(None, description="Price per unit")
    discount: Optional[FieldValue] = Field(None, description="Discount amount or percentage")
    tax_rate: Optional[FieldValue] = Field(None, description="Tax rate applied to this line")
    total: Optional[FieldValue] = Field(None, description="Line item total amount")


class InvoiceMetadata(BaseModel):
    """
    Metadata about the extraction process and source document.

    Tracks processing details, model version, and aggregate quality metrics.
    Supports multiple timestamp formats and processing time units for compatibility.

    Attributes:
        source_file_name: Original filename of the uploaded document (required)
        source_format: Detected format category: pdf, image, or text (optional)
        model_version: GPT model version used for extraction (default: gpt-4o-2024-08-06)
        extraction_time: ISO timestamp when extraction completed (optional)
        parse_timestamp: Alternative timestamp format (optional)
        processing_time_ms: Processing duration in milliseconds (optional)
        processing_time_seconds: Processing duration in seconds (optional)
        overall_confidence: Aggregate confidence score across all fields [0.0-1.0] (optional)
        warning: Any warnings or notices about extraction quality (optional)

    Example:
        meta = InvoiceMetadata(
            source_file_name="invoice_20240115.pdf",
            source_format="pdf",
            model_version="gpt-4o-2024-08-06",
            processing_time_seconds=2.5,
            overall_confidence=0.94,
            warning="Low confidence on supplier tax_id field"
        )
    """
    source_file_name: str = Field(..., description="Original filename of uploaded document")
    source_format: Optional[Literal["pdf", "image", "text"]] = Field(
        None,
        description="Detected format category"
    )
    model_version: str = Field(
        default="gpt-4o-2024-08-06",
        description="GPT model version used for extraction"
    )
    extraction_time: Optional[datetime] = Field(None, description="ISO timestamp when extraction completed")
    parse_timestamp: Optional[str] = Field(None, description="Alternative timestamp format")
    processing_time_ms: Optional[int] = Field(None, description="Processing duration in milliseconds")
    processing_time_seconds: Optional[float] = Field(None, description="Processing duration in seconds")
    overall_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Aggregate confidence score across all fields [0.0-1.0]"
    )
    warning: Optional[str] = Field(None, description="Warnings or notices about extraction quality")


class InvoiceResponse(BaseModel):
    """
    Complete invoice extraction response.

    This is the top-level response schema returned by the /parse endpoint.
    Contains all extracted invoice data organized by section, plus metadata
    about the extraction process.

    Attributes:
        supplier: Supplier/vendor information (required)
        customer: Customer/buyer information (required)
        invoice: Invoice header and summary (required)
        line_items: List of invoice line items (default: empty list, max: 50 items)
        meta: Extraction metadata and quality metrics (required)

    Example:
        response = InvoiceResponse(
            supplier=SupplierInfo(...),
            customer=CustomerInfo(...),
            invoice=InvoiceSummary(...),
            line_items=[LineItem(...), LineItem(...)],
            meta=InvoiceMetadata(...)
        )
    """
    supplier: SupplierInfo = Field(..., description="Supplier/vendor information")
    customer: CustomerInfo = Field(..., description="Customer/buyer information")
    invoice: InvoiceSummary = Field(..., description="Invoice header and summary")
    line_items: List[LineItem] = Field(
        default_factory=list,
        max_length=50,
        description="List of invoice line items (max: 50)"
    )
    meta: InvoiceMetadata = Field(..., description="Extraction metadata and quality metrics")


class ErrorDetail(BaseModel):
    """
    Detailed error information for API error responses.

    Attributes:
        code: Machine-readable error code (e.g., FILE_TOO_LARGE, INVALID_FORMAT)
        message: Human-readable error description
        details: Additional context about the error (optional)

    Example:
        error = ErrorDetail(
            code="FILE_TOO_LARGE",
            message="File size exceeds maximum allowed size of 5MB",
            details={"file_size_mb": 7.2, "max_size_mb": 5}
        )
    """
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[dict] = Field(None, description="Additional error context")


class ErrorResponse(BaseModel):
    """
    Standard error response wrapper.

    All API errors return this consistent structure for easier client-side handling.

    Attributes:
        error: Detailed error information

    Example:
        error_response = ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid file format",
                details={"allowed_types": ["pdf", "png", "jpg"]}
            )
        )
    """
    error: ErrorDetail = Field(..., description="Detailed error information")
