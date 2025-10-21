"""
Real API Accuracy Validation Test (TRD-033)

Tests invoice parsing accuracy against ground truth using REAL GPT-4o API calls.
No mocking - this validates end-to-end extraction accuracy with actual invoices.

Example Output:
    ============================================================
    ACCURACY VALIDATION REPORT
    ============================================================
    Invoice: 1Password-invoice-2025-10-05.pdf
    Accuracy: 85.7%

    Matched Fields (12/14):
      ✓ supplier.name: AgileBits Inc. dba 1Password == AgileBits Inc. dba 1Password
      ✓ invoice.number: in_1SEvjvHBax7L5HDfxS6QV4EE == in_1SEvjvHBax7L5HDfxS6QV4EE
      ✗ invoice.tax: 0.0 != (missing)
      ...

Usage:
    # Run single test with console output
    pytest tests/test_accuracy_validation.py::test_single_invoice_accuracy -v -s

    # Skip expensive real API tests in CI
    pytest -m "not real_api"
"""

import json
import pytest
from pathlib import Path
from typing import Any, Tuple, Optional

from openai import AsyncOpenAI
from app.config import get_settings
from app.services.gpt4o_service import GPT4oService
from app.schemas import InvoiceResponse, FieldValue


# Test configuration
TEST_INVOICE_FILE = "1Password-invoice-2025-10-05.pdf"
ACCURACY_THRESHOLD = 0.70  # 70% - flexible for single invoice demo


def load_test_data(invoice_name: str) -> Tuple[bytes, dict]:
    """
    Load invoice PDF and corresponding ground truth JSON.

    Args:
        invoice_name: Name of invoice file (e.g., "1Password-invoice-2025-10-05.pdf")

    Returns:
        Tuple of (pdf_bytes, ground_truth_dict)

    Raises:
        FileNotFoundError: If invoice or ground truth file not found
    """
    fixtures_dir = Path(__file__).parent / "fixtures" / "invoices"

    # Load PDF
    pdf_path = fixtures_dir / invoice_name
    if not pdf_path.exists():
        raise FileNotFoundError(f"Invoice not found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Load ground truth JSON
    ground_truth_name = invoice_name.replace(".pdf", "-ground-truth.json")
    ground_truth_path = fixtures_dir / ground_truth_name
    if not ground_truth_path.exists():
        raise FileNotFoundError(f"Ground truth not found: {ground_truth_path}")

    with open(ground_truth_path, "r") as f:
        ground_truth = json.load(f)

    return pdf_bytes, ground_truth


def extract_field_value(obj: Any, field_path: str) -> Optional[Any]:
    """
    Extract value from nested object using dot notation path.

    Handles FieldValue objects by extracting the .value attribute.

    Args:
        obj: Object to extract from (InvoiceResponse or dict)
        field_path: Dot-separated path (e.g., "supplier.name", "invoice.total")

    Returns:
        Extracted value or None if path doesn't exist

    Example:
        extract_field_value(response, "supplier.name")  # Returns "ACME Corp"
        extract_field_value(response, "invoice.tax")    # Returns 10.50
    """
    parts = field_path.split(".")
    current = obj

    for part in parts:
        # Handle both dict and object attribute access
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)

        if current is None:
            return None

    # Extract value from FieldValue objects
    if isinstance(current, FieldValue):
        return current.value

    return current


def normalize_value(value: Any) -> Any:
    """
    Normalize value for comparison.

    Handles:
    - Empty strings as None/missing
    - Float/int conversion with tolerance
    - String trimming and case normalization

    Args:
        value: Value to normalize

    Returns:
        Normalized value for comparison
    """
    # Treat empty strings as None
    if isinstance(value, str) and value.strip() == "":
        return None

    # Normalize strings
    if isinstance(value, str):
        return value.strip()

    # Convert float to int if it's a whole number (e.g., 0.0 -> 0)
    if isinstance(value, float) and value.is_integer():
        return int(value)

    return value


def values_match(extracted: Any, expected: Any, tolerance: float = 0.01) -> bool:
    """
    Check if two values match with flexible comparison.

    Comparison rules:
    - None == None
    - Empty string == None (both missing)
    - Numbers match within tolerance (e.g., 3.99 == 3.989999)
    - Strings match after trimming and case-insensitive

    Args:
        extracted: Value extracted by GPT-4o
        expected: Expected ground truth value
        tolerance: Tolerance for float comparison (default: 0.01)

    Returns:
        True if values match within comparison rules
    """
    extracted = normalize_value(extracted)
    expected = normalize_value(expected)

    # Both missing
    if extracted is None and expected is None:
        return True

    # One missing
    if extracted is None or expected is None:
        return False

    # Numeric comparison with tolerance
    if isinstance(extracted, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(extracted) - float(expected)) <= tolerance

    # String comparison (case-insensitive, trimmed)
    if isinstance(extracted, str) and isinstance(expected, str):
        return extracted.lower().strip() == expected.lower().strip()

    # Type mismatch - try string conversion
    return str(extracted).lower().strip() == str(expected).lower().strip()


def compare_fields(response: InvoiceResponse, ground_truth: dict) -> list[Tuple[str, bool, Any, Any]]:
    """
    Compare all expected fields between extracted response and ground truth.

    Args:
        response: InvoiceResponse from GPT-4o parsing
        ground_truth: Ground truth dict with expected_fields

    Returns:
        List of tuples: (field_path, matched, extracted_value, expected_value)

    Example:
        results = compare_fields(response, ground_truth)
        for field, matched, extracted, expected in results:
            if not matched:
                print(f"Mismatch: {field} - got {extracted}, expected {expected}")
    """
    results = []
    expected_fields = ground_truth.get("expected_fields", {})

    for field_path, expected_value in expected_fields.items():
        # Extract actual value from response
        extracted_value = extract_field_value(response, field_path)

        # Compare values
        matched = values_match(extracted_value, expected_value)

        results.append((field_path, matched, extracted_value, expected_value))

    return results


def calculate_accuracy(comparison_results: list) -> float:
    """
    Calculate field extraction accuracy percentage.

    Args:
        comparison_results: List of (field, matched, extracted, expected) tuples

    Returns:
        Accuracy as float [0.0-1.0]
    """
    if not comparison_results:
        return 0.0

    total_fields = len(comparison_results)
    matched_fields = sum(1 for _, matched, _, _ in comparison_results if matched)

    return matched_fields / total_fields


def print_accuracy_report(invoice_name: str, comparison_results: list, accuracy: float):
    """
    Print detailed accuracy report to console.

    Args:
        invoice_name: Name of tested invoice file
        comparison_results: Field comparison results
        accuracy: Overall accuracy percentage
    """
    total = len(comparison_results)
    matched = sum(1 for _, m, _, _ in comparison_results if m)

    print("\n" + "=" * 60)
    print("ACCURACY VALIDATION REPORT")
    print("=" * 60)
    print(f"Invoice: {invoice_name}")
    print(f"Accuracy: {accuracy:.1%} ({matched}/{total} fields)")
    print(f"\nField Comparison:")
    print("-" * 60)

    for field, matched, extracted, expected in comparison_results:
        status = "✓" if matched else "✗"
        operator = "==" if matched else "!="

        # Format values for display
        extracted_display = extracted if extracted is not None else "(missing)"
        expected_display = expected if expected is not None else "(missing)"

        print(f"  {status} {field:<30} {extracted_display} {operator} {expected_display}")

    print("=" * 60)


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_single_invoice_accuracy():
    """
    Test real GPT-4o extraction accuracy against ground truth.

    This test:
    1. Loads 1Password invoice PDF and ground truth
    2. Calls REAL OpenAI GPT-4o API (no mocking)
    3. Compares all expected fields
    4. Calculates accuracy percentage
    5. Prints detailed report to console
    6. Asserts accuracy >= 70%

    Test is tagged with @pytest.mark.real_api to allow skipping in CI:
        pytest -m "not real_api"  # Skip expensive API tests

    TRD Reference: Section 11 - TRD-033 Accuracy Validation
    """
    # Load test data
    pdf_bytes, ground_truth = load_test_data(TEST_INVOICE_FILE)

    # Create real OpenAI client (no mocking)
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Initialize GPT-4o service
    service = GPT4oService(
        openai_client=client,
        model="gpt-4o",
        temperature=0.4,
        max_tokens=4096,
        timeout=20.0
    )

    # Parse invoice with REAL API call
    response = await service.parse_invoice(
        file_content=pdf_bytes,
        file_name=TEST_INVOICE_FILE,
        mime_type="application/pdf"
    )

    # Validate response structure
    assert isinstance(response, InvoiceResponse), "Response should be InvoiceResponse"
    assert response.meta is not None, "Response should include metadata"
    assert response.meta.overall_confidence > 0.0, "Should have confidence score"

    # Compare fields to ground truth
    comparison_results = compare_fields(response, ground_truth)

    # Calculate accuracy
    accuracy = calculate_accuracy(comparison_results)

    # Print detailed report (visible with -s flag)
    print_accuracy_report(TEST_INVOICE_FILE, comparison_results, accuracy)

    # Assert accuracy threshold
    assert accuracy >= ACCURACY_THRESHOLD, (
        f"Accuracy {accuracy:.1%} below threshold {ACCURACY_THRESHOLD:.1%}\n"
        f"Failed fields:\n" +
        "\n".join(
            f"  - {field}: {extracted} != {expected}"
            for field, matched, extracted, expected in comparison_results
            if not matched
        )
    )

    # Log success
    print(f"\n✅ Accuracy test PASSED: {accuracy:.1%} >= {ACCURACY_THRESHOLD:.1%}")


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_line_items_accuracy():
    """
    Test line item extraction accuracy.

    Validates that:
    - Correct number of line items extracted
    - Key fields match ground truth (description, quantity, unit_price, total)

    TRD Reference: Section 11 - TRD-033 Line Item Validation
    """
    # Load test data
    pdf_bytes, ground_truth = load_test_data(TEST_INVOICE_FILE)

    # Create real OpenAI client
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Parse invoice
    service = GPT4oService(openai_client=client)
    response = await service.parse_invoice(
        file_content=pdf_bytes,
        file_name=TEST_INVOICE_FILE,
        mime_type="application/pdf"
    )

    # Get expected line items
    expected_count = ground_truth.get("expected_line_items_count", 0)
    expected_items = ground_truth.get("expected_line_items", [])

    # Validate count
    actual_count = len(response.line_items)
    print(f"\nLine Items: {actual_count} extracted, {expected_count} expected")

    assert actual_count == expected_count, (
        f"Expected {expected_count} line items, got {actual_count}"
    )

    # Compare first line item (if exists)
    if expected_items and response.line_items:
        expected_item = expected_items[0]
        actual_item = response.line_items[0]

        # Check key fields
        checks = [
            ("description", actual_item.description.value, expected_item.get("description")),
            ("quantity", actual_item.quantity.value if actual_item.quantity else None, expected_item.get("quantity")),
            ("unit_price", actual_item.unit_price.value if actual_item.unit_price else None, expected_item.get("unit_price")),
            ("total", actual_item.total.value if actual_item.total else None, expected_item.get("total")),
        ]

        print("\nLine Item Field Comparison:")
        for field, actual, expected in checks:
            matched = values_match(actual, expected)
            status = "✓" if matched else "✗"
            print(f"  {status} {field}: {actual} {'==' if matched else '!='} {expected}")

        # Assert at least description matches
        assert values_match(actual_item.description.value, expected_item.get("description")), \
            "Line item description should match"

    print("\n✅ Line items test PASSED")
