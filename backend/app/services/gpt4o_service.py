"""
GPT-4o Invoice Parsing Service (TRD Section 6)

Integrates with OpenAI's GPT-4o API to extract structured invoice data from
PDF, image, and text files using semantic understanding and OCR capabilities.

Example Usage:
    ```python
    from openai import AsyncOpenAI
    from app.services.gpt4o_service import GPT4oService

    client = AsyncOpenAI(api_key="sk-...")
    service = GPT4oService(
        openai_client=client,
        model="gpt-4o",
        temperature=0.4,
        max_tokens=4096,
        timeout=20.0
    )

    # Parse invoice
    result = await service.parse_invoice(
        file_content=pdf_bytes,
        file_name="invoice.pdf",
        mime_type="application/pdf"
    )
    print(result.invoice.number.value)  # "INV-2024-001"
    ```

TRD References:
- Section 6: GPT-4o Integration Architecture
- Section 6.1: Prompt Engineering Strategy
- Section 6.2: Error Handling & Retry Logic
- NFR-001: Parse time ≤20s
"""

import json
import base64
import time
import logging
from typing import Optional
from openai import AsyncOpenAI
from app.schemas import InvoiceResponse, InvoiceMetadata
from app.utils.retry import retry_with_exponential_backoff

logger = logging.getLogger(__name__)


class InvoiceParsingError(Exception):
    """
    Custom exception for invoice parsing failures.

    Raised when GPT-4o API returns invalid data, parsing fails,
    or validation errors occur during invoice extraction.

    Example:
        raise InvoiceParsingError("Failed to parse GPT-4o response: malformed JSON")
    """
    pass


class GPT4oService:
    """
    Service for parsing invoices using OpenAI's GPT-4o model.

    Handles file format detection, prompt engineering, API integration,
    retry logic, and response validation. Supports PDF, image (JPEG/PNG),
    and plain text invoice formats.

    Attributes:
        client: AsyncOpenAI client instance for API calls
        model: GPT model name (default: "gpt-4o")
        temperature: Model temperature for response consistency (default: 0.4)
        max_tokens: Maximum response tokens (default: 4096)
        timeout: Request timeout in seconds (default: 20.0)

    TRD Reference: Section 6 - GPT-4o Integration Architecture
    """

    def __init__(
        self,
        openai_client: AsyncOpenAI,
        model: str = "gpt-4o",
        temperature: float = 0.4,
        max_tokens: int = 4096,
        timeout: float = 20.0,
    ):
        """
        Initialize GPT-4o service with OpenAI client and configuration.

        Args:
            openai_client: Configured AsyncOpenAI client instance
            model: GPT model to use (default: "gpt-4o")
            temperature: Sampling temperature [0.0-1.0] (default: 0.4 for balanced consistency)
            max_tokens: Maximum tokens in response (default: 4096 for complex invoices)
            timeout: API call timeout in seconds (default: 20.0 per NFR-001)
        """
        self.client = openai_client
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    async def parse_invoice(
        self,
        file_content: bytes,
        file_name: str,
        mime_type: str,
    ) -> InvoiceResponse:
        """
        Parse invoice file into structured InvoiceResponse.

        Detects file format, constructs appropriate GPT-4o prompt with vision
        capabilities for images/PDFs, calls API with retry logic, and validates
        response against schema.

        Args:
            file_content: Raw file bytes (PDF, image, or text)
            file_name: Original filename for metadata
            mime_type: MIME type (application/pdf, image/jpeg, image/png, text/plain)

        Returns:
            InvoiceResponse: Structured invoice data with confidence scores and metadata

        Raises:
            InvoiceParsingError: If parsing fails, response is malformed, or validation fails
            APITimeoutError: If request exceeds timeout (20s per NFR-001)
            RateLimitError: If OpenAI rate limit exceeded (after retries)

        Example:
            result = await service.parse_invoice(
                file_content=pdf_bytes,
                file_name="invoice.pdf",
                mime_type="application/pdf"
            )

        TRD Reference: Section 6.1 - Invoice extraction implementation
        """
        start_time = time.time()

        # Detect source format from MIME type
        source_format = self._detect_format(mime_type)

        # Build messages for GPT-4o
        messages = self._build_messages(file_content, mime_type, source_format)

        try:
            # Call GPT-4o API with retry logic (Section 6.2)
            response = await retry_with_exponential_backoff(
                self.client.chat.completions.create,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                messages=messages,
            )

            # Extract JSON content from response
            content = response.choices[0].message.content

            # Parse JSON response
            try:
                invoice_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT-4o JSON response: {e}")
                raise InvoiceParsingError(
                    f"GPT-4o returned malformed JSON: {str(e)}"
                )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Add metadata to response
            invoice_data["meta"] = self._build_metadata(
                source_file_name=file_name,
                source_format=source_format,
                model_version=response.model,
                processing_time_seconds=processing_time,
                invoice_data=invoice_data,
            )

            # Validate and parse into InvoiceResponse schema
            try:
                invoice_response = InvoiceResponse(**invoice_data)
            except Exception as e:
                logger.error(f"Failed to validate invoice response schema: {e}")
                raise InvoiceParsingError(
                    f"Invalid response structure: {str(e)}"
                )

            logger.info(
                f"Successfully parsed invoice '{file_name}' in {processing_time:.2f}s "
                f"with overall confidence {invoice_response.meta.overall_confidence:.2f}"
            )

            return invoice_response

        except InvoiceParsingError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            # Catch and wrap any other errors
            logger.error(f"Unexpected error parsing invoice: {type(e).__name__}: {e}")
            raise InvoiceParsingError(
                f"Failed to parse invoice: {type(e).__name__}: {str(e)}"
            )

    def _detect_format(self, mime_type: str) -> str:
        """
        Detect invoice format category from MIME type.

        Args:
            mime_type: MIME type string (e.g., "application/pdf")

        Returns:
            Format category: "pdf", "image", or "text"

        Example:
            _detect_format("image/jpeg")  # Returns "image"
        """
        if mime_type == "application/pdf":
            return "pdf"
        elif mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("text/"):
            return "text"
        else:
            # Default to text for unknown types
            return "text"

    def _build_messages(
        self,
        file_content: bytes,
        mime_type: str,
        source_format: str,
    ) -> list:
        """
        Build GPT-4o messages array with appropriate content format.

        For images and PDFs, includes base64-encoded file data for vision processing.
        For text files, includes decoded text content directly.

        Args:
            file_content: Raw file bytes
            mime_type: MIME type for vision API
            source_format: Detected format category

        Returns:
            List of message dictionaries for OpenAI API

        TRD Reference: Section 6.1 - Prompt engineering
        """
        # System prompt with extraction instructions
        system_prompt = self._build_extraction_prompt()

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Build user message based on format
        if source_format in ["pdf", "image"]:
            # Use vision capabilities for PDF and images
            base64_content = base64.b64encode(file_content).decode("utf-8")
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please extract all invoice information from this document according to the schema provided."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_content}"
                        }
                    }
                ]
            }
        else:
            # Plain text - decode and include directly
            try:
                text_content = file_content.decode("utf-8")
            except UnicodeDecodeError:
                # Fallback to latin-1 if UTF-8 fails
                text_content = file_content.decode("latin-1")

            user_message = {
                "role": "user",
                "content": f"Please extract all invoice information from this text:\n\n{text_content}"
            }

        messages.append(user_message)
        return messages

    def _build_extraction_prompt(self) -> str:
        """
        Build comprehensive extraction prompt for GPT-4o.

        Instructs the model to extract all invoice fields with confidence scores
        and return JSON matching the InvoiceResponse schema structure.

        Returns:
            System prompt string with schema and instructions

        TRD Reference: Section 6.1 - Prompt engineering strategy
        """
        prompt = """You are an expert invoice data extraction system. Extract all information from the provided invoice document and return it as JSON.

REQUIRED OUTPUT FORMAT:
Return ONLY valid JSON (no markdown, no code blocks, no explanatory text) matching this exact schema:

{
  "supplier": {
    "name": {"value": "string", "confidence": 0.0-1.0},
    "address": {"value": "string", "confidence": 0.0-1.0} (optional),
    "phone": {"value": "string", "confidence": 0.0-1.0} (optional),
    "email": {"value": "string", "confidence": 0.0-1.0} (optional),
    "tax_id": {"value": "string", "confidence": 0.0-1.0} (optional)
  },
  "customer": {
    "name": {"value": "string", "confidence": 0.0-1.0},
    "address": {"value": "string", "confidence": 0.0-1.0} (optional),
    "account_id": {"value": "string", "confidence": 0.0-1.0} (optional)
  },
  "invoice": {
    "number": {"value": "string", "confidence": 0.0-1.0},
    "issue_date": {"value": "YYYY-MM-DD", "confidence": 0.0-1.0},
    "due_date": {"value": "YYYY-MM-DD", "confidence": 0.0-1.0},
    "currency": {"value": "string", "confidence": 0.0-1.0} (optional),
    "subtotal": {"value": number, "confidence": 0.0-1.0} (optional),
    "tax_amount": {"value": number, "confidence": 0.0-1.0} (optional),
    "total_amount": {"value": number, "confidence": 0.0-1.0} (optional),
    "payment_terms": {"value": "string", "confidence": 0.0-1.0} (optional),
    "po_number": {"value": "string", "confidence": 0.0-1.0} (optional)
  },
  "line_items": [
    {
      "sku": {"value": "string", "confidence": 0.0-1.0} (optional),
      "description": {"value": "string", "confidence": 0.0-1.0},
      "quantity": {"value": number, "confidence": 0.0-1.0} (optional),
      "unit_price": {"value": number, "confidence": 0.0-1.0} (optional),
      "discount": {"value": number, "confidence": 0.0-1.0} (optional),
      "tax_rate": {"value": number, "confidence": 0.0-1.0} (optional),
      "total": {"value": number, "confidence": 0.0-1.0} (optional)
    }
  ]
}

EXTRACTION GUIDELINES:
1. REQUIRED FIELDS (always extract): supplier.name, customer.name, invoice.number, invoice.issue_date, invoice.due_date
2. OPTIONAL FIELDS: All other fields - only include if clearly present in the document
3. CONFIDENCE SCORES:
   - 1.0 = Absolutely certain (printed clearly, no ambiguity)
   - 0.9-0.99 = Very confident (clear but minor uncertainty)
   - 0.7-0.89 = Confident (readable but some interpretation needed)
   - 0.5-0.69 = Moderate confidence (unclear or partially obscured)
   - 0.0-0.49 = Low confidence (guessing or very unclear)
4. DATE FORMAT: Always use YYYY-MM-DD format for dates
5. NUMBERS: Extract as numeric values (not strings) for amounts, quantities, prices
6. MISSING DATA: Omit optional fields entirely if not present (do not include null/empty values)
7. LINE ITEMS: Extract up to 50 line items maximum

Return ONLY the JSON object, no additional text or formatting."""
        return prompt

    def _build_metadata(
        self,
        source_file_name: str,
        source_format: str,
        model_version: str,
        processing_time_seconds: float,
        invoice_data: dict,
    ) -> dict:
        """
        Build metadata dictionary for InvoiceResponse.

        Calculates overall confidence score by averaging all field confidence
        scores across the invoice data.

        Args:
            source_file_name: Original filename
            source_format: Format category (pdf/image/text)
            model_version: GPT model version from API response
            processing_time_seconds: Time taken to parse invoice
            invoice_data: Parsed invoice data for confidence calculation

        Returns:
            Metadata dictionary for InvoiceMetadata model

        TRD Reference: Section 5.1 - Metadata requirements
        """
        # Calculate overall confidence from all fields
        overall_confidence = self._calculate_overall_confidence(invoice_data)

        return {
            "source_file_name": source_file_name,
            "source_format": source_format,
            "model_version": model_version,
            "processing_time_seconds": round(processing_time_seconds, 3),
            "overall_confidence": round(overall_confidence, 2),
        }

    def _calculate_overall_confidence(self, invoice_data: dict) -> float:
        """
        Calculate aggregate confidence score across all extracted fields.

        Recursively traverses invoice data to find all confidence scores
        and returns their average.

        Args:
            invoice_data: Parsed invoice dictionary with nested FieldValue objects

        Returns:
            Average confidence score [0.0-1.0]

        Example:
            data = {"supplier": {"name": {"value": "ACME", "confidence": 0.9}}}
            _calculate_overall_confidence(data)  # Returns 0.9
        """
        confidence_scores = []

        def extract_confidences(obj):
            """Recursively extract all confidence scores from nested structure."""
            if isinstance(obj, dict):
                # Check if this is a FieldValue object
                if "confidence" in obj:
                    confidence_scores.append(obj["confidence"])
                # Recurse into nested objects
                for value in obj.values():
                    extract_confidences(value)
            elif isinstance(obj, list):
                # Recurse into list items
                for item in obj:
                    extract_confidences(item)

        # Extract all confidence scores
        extract_confidences(invoice_data)

        # Calculate average
        if not confidence_scores:
            return 0.0
        return sum(confidence_scores) / len(confidence_scores)
