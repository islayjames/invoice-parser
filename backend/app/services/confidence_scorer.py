"""
Confidence Scoring Service (TRD Section 7.3)

Validates invoice extraction results based on confidence scores.
Rejects invoices where critical fields have <50% confidence.

TRD References:
- Section 7.3: Confidence-based validation
- NFR-005: Field accuracy ≥90%
"""

import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


# Critical fields that must have ≥50% confidence
CRITICAL_FIELDS = [
    "supplier.name",
    "customer.name",
    "invoice.number",
    "invoice.issue_date",
    "invoice.due_date",
    "invoice.total_amount",
]

# Warning threshold for moderate confidence (50-90%)
WARNING_THRESHOLD = 0.90
REJECTION_THRESHOLD = 0.50


def validate_confidence(invoice_data: dict) -> Tuple[bool, Optional[str], float]:
    """
    Validate invoice data based on confidence scores for critical fields.

    Ensures all critical fields have confidence ≥50%. Logs warnings for
    fields with confidence between 50-90%. Calculates overall confidence
    score across all extracted fields.

    Args:
        invoice_data: Parsed invoice dictionary with nested FieldValue objects
                      containing 'value' and 'confidence' keys

    Returns:
        Tuple of (is_valid, error_message, overall_confidence):
            - is_valid: True if all critical fields pass validation
            - error_message: Description of failure if is_valid=False, else None
            - overall_confidence: Average confidence score across all fields [0.0-1.0]

    Example:
        is_valid, error, score = validate_confidence(invoice_data)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error)

    TRD Reference: Section 7.3 - Confidence validation
    """
    warnings = []

    # Check all critical fields
    for field_path in CRITICAL_FIELDS:
        confidence = _get_field_confidence(invoice_data, field_path)

        if confidence is None:
            # Critical field is missing
            error_msg = (
                f"Critical field '{field_path}' is missing or not extracted. "
                f"Cannot process invoice without this required information."
            )
            logger.error(error_msg)
            return False, error_msg, 0.0

        if confidence < REJECTION_THRESHOLD:
            # Critical field has too low confidence
            error_msg = (
                f"Critical field '{field_path}' has insufficient confidence "
                f"({confidence:.2f} < {REJECTION_THRESHOLD}). Invoice quality "
                f"too low for reliable processing."
            )
            logger.error(error_msg)
            return False, error_msg, _calculate_overall_confidence(invoice_data)

        if confidence < WARNING_THRESHOLD:
            # Moderate confidence - log warning but don't reject
            warning_msg = (
                f"Field '{field_path}' has moderate confidence ({confidence:.2f}). "
                f"Manual review may be needed."
            )
            warnings.append(warning_msg)
            logger.warning(warning_msg)

    # Calculate overall confidence score
    overall_confidence = _calculate_overall_confidence(invoice_data)

    # Log warnings if any
    if warnings:
        logger.info(
            f"Invoice passed validation with {len(warnings)} warning(s). "
            f"Overall confidence: {overall_confidence:.2f}"
        )
    else:
        logger.info(
            f"Invoice passed validation with high confidence. "
            f"Overall confidence: {overall_confidence:.2f}"
        )

    return True, None, overall_confidence


def _get_field_confidence(invoice_data: dict, field_path: str) -> Optional[float]:
    """
    Extract confidence score for a specific field from nested invoice data.

    Traverses nested dictionary structure using dot-notation path
    (e.g., "supplier.name" → invoice_data["supplier"]["name"]["confidence"]).

    Args:
        invoice_data: Nested invoice dictionary
        field_path: Dot-notation path to field (e.g., "supplier.name")

    Returns:
        Confidence score [0.0-1.0] if field exists, None if field is missing

    Example:
        confidence = _get_field_confidence(data, "supplier.name")
        # Returns 0.95 if data = {"supplier": {"name": {"value": "ACME", "confidence": 0.95}}}
    """
    parts = field_path.split(".")
    current = invoice_data

    try:
        # Navigate through nested structure
        for part in parts:
            if part not in current:
                return None
            current = current[part]

        # Check if we reached a FieldValue object with confidence
        if isinstance(current, dict) and "confidence" in current:
            return current["confidence"]
        else:
            # Field exists but doesn't have confidence score
            logger.warning(f"Field '{field_path}' exists but has no confidence score")
            return None

    except (KeyError, TypeError):
        # Field path is invalid or data structure is unexpected
        return None


def _calculate_overall_confidence(invoice_data: dict) -> float:
    """
    Calculate aggregate confidence score across all extracted fields.

    Recursively traverses invoice data to find all confidence scores
    and returns their average.

    Args:
        invoice_data: Parsed invoice dictionary with nested FieldValue objects

    Returns:
        Average confidence score [0.0-1.0]

    Example:
        data = {
            "supplier": {"name": {"value": "ACME", "confidence": 0.9}},
            "invoice": {"number": {"value": "INV-001", "confidence": 0.8}}
        }
        _calculate_overall_confidence(data)  # Returns 0.85
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
        logger.warning("No confidence scores found in invoice data")
        return 0.0

    return sum(confidence_scores) / len(confidence_scores)
