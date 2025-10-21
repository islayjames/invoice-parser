"""
Pydantic schema models for invoice parsing API (TRD Section 5.1)

Defines the data structures for invoice extraction responses and error handling.
"""

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
    currency: Optional[FieldValue] = None
    subtotal: Optional[FieldValue] = None
    tax: Optional[FieldValue] = None
    total: Optional[FieldValue] = None
    total_amount: Optional[FieldValue] = None
    tax_amount: Optional[FieldValue] = None
    payment_terms: Optional[FieldValue] = None
    po_number: Optional[FieldValue] = None

    @field_validator('currency')
    def default_currency(cls, v):
        if v is None:
            return None
        if v.value is None or v.value == "":
            v.value = "USD"
        return v


class LineItem(BaseModel):
    sku: Optional[FieldValue] = None
    description: FieldValue
    quantity: Optional[FieldValue] = None
    unit_price: Optional[FieldValue] = None
    discount: Optional[FieldValue] = None
    tax_rate: Optional[FieldValue] = None
    total: Optional[FieldValue] = None


class InvoiceMetadata(BaseModel):
    source_file_name: str
    source_format: Optional[Literal["pdf", "image", "text"]] = None
    model_version: str = "gpt-4o-2024-08-06"
    extraction_time: Optional[datetime] = None
    parse_timestamp: Optional[str] = None
    processing_time_ms: Optional[int] = None
    processing_time_seconds: Optional[float] = None
    overall_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
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
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
