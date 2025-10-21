#!/usr/bin/env python3
"""
Multi-Invoice Accuracy Test Runner

Runs accuracy validation tests against multiple invoices and generates
a summary report comparing extraction accuracy across different invoice types.

Usage:
    python test_multiple_invoices.py

TRD Reference: Section 11 - TRD-033 Accuracy Validation
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
from openai import AsyncOpenAI

from app.config import get_settings
from app.services.gpt4o_service import GPT4oService
from app.schemas import InvoiceResponse

# Import test utilities from test file
import sys
sys.path.insert(0, str(Path(__file__).parent / "tests"))
from test_accuracy_validation import (
    load_test_data,
    compare_fields,
    calculate_accuracy,
    print_accuracy_report
)


# Invoices to test (selected for variety)
TEST_INVOICES = [
    "1Password-invoice-2025-10-05.pdf",      # 46KB - Small, simple subscription
    "5373941515.pdf",                         # 91KB - Medium size
    "Atlassian_Invoice_IN-003-942-505.pdf",  # 65KB - Software vendor
]


async def test_single_invoice(
    invoice_name: str,
    service: GPT4oService
) -> Dict[str, Any]:
    """
    Test accuracy for a single invoice.

    Returns:
        Dict with accuracy results and metadata
    """
    print(f"\n{'='*60}")
    print(f"Testing: {invoice_name}")
    print(f"{'='*60}")

    try:
        # Load test data
        pdf_bytes, ground_truth = load_test_data(invoice_name)

        # Parse invoice with REAL API call
        response = await service.parse_invoice(
            file_content=pdf_bytes,
            file_name=invoice_name,
            mime_type="application/pdf"
        )

        # Compare fields to ground truth
        comparison_results = compare_fields(response, ground_truth)

        # Calculate accuracy
        accuracy = calculate_accuracy(comparison_results)

        # Print detailed report
        print_accuracy_report(invoice_name, comparison_results, accuracy)

        # Collect results
        return {
            "invoice": invoice_name,
            "size_kb": len(pdf_bytes) / 1024,
            "accuracy": accuracy,
            "fields_tested": len(comparison_results),
            "fields_matched": sum(1 for r in comparison_results if r["matched"]),
            "processing_time": response.meta.processing_time_seconds,
            "overall_confidence": response.meta.overall_confidence,
            "success": True,
            "error": None,
            "comparison_results": comparison_results
        }

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        return {
            "invoice": invoice_name,
            "success": False,
            "error": str(e),
            "accuracy": 0.0
        }


async def main():
    """Run accuracy tests across multiple invoices and generate summary."""

    print("\n" + "="*60)
    print("MULTI-INVOICE ACCURACY VALIDATION")
    print("="*60)
    print(f"Testing {len(TEST_INVOICES)} invoices with real GPT-4o API calls")
    print("="*60)

    # Initialize GPT-4o service
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    service = GPT4oService(
        openai_client=client,
        model="gpt-4o",
        temperature=0.4,
        max_tokens=4096,
        timeout=20.0
    )

    # Test each invoice
    results = []
    for invoice_name in TEST_INVOICES:
        result = await test_single_invoice(invoice_name, service)
        results.append(result)

        # Brief pause between API calls to avoid rate limiting
        if invoice_name != TEST_INVOICES[-1]:
            await asyncio.sleep(2)

    # Generate summary report
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)

    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]

    if successful_tests:
        avg_accuracy = sum(r["accuracy"] for r in successful_tests) / len(successful_tests)
        avg_processing_time = sum(r["processing_time"] for r in successful_tests) / len(successful_tests)
        avg_confidence = sum(r["overall_confidence"] for r in successful_tests) / len(successful_tests)

        print(f"\n✅ Successful Tests: {len(successful_tests)}/{len(results)}")
        print(f"❌ Failed Tests: {len(failed_tests)}/{len(results)}")
        print(f"\n📊 Average Accuracy: {avg_accuracy:.1%}")
        print(f"⏱️  Average Processing Time: {avg_processing_time:.2f}s")
        print(f"🎯 Average Confidence: {avg_confidence:.1%}")

        print("\n" + "-"*60)
        print("Individual Results:")
        print("-"*60)
        for r in successful_tests:
            status = "✅" if r["accuracy"] >= 0.70 else "⚠️"
            print(f"{status} {r['invoice']:<45} {r['accuracy']:>6.1%} ({r['fields_matched']}/{r['fields_tested']} fields)")

        # Find common failure patterns
        print("\n" + "-"*60)
        print("Common Field Issues:")
        print("-"*60)

        field_failures = {}
        for r in successful_tests:
            for comp in r.get("comparison_results", []):
                if not comp["matched"]:
                    field = comp["field"]
                    if field not in field_failures:
                        field_failures[field] = 0
                    field_failures[field] += 1

        # Sort by frequency
        sorted_failures = sorted(field_failures.items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_failures[:10]:  # Top 10
            percentage = (count / len(successful_tests)) * 100
            print(f"  • {field:<35} Failed in {count}/{len(successful_tests)} invoices ({percentage:.0f}%)")

    if failed_tests:
        print("\n" + "-"*60)
        print("Failed Tests:")
        print("-"*60)
        for r in failed_tests:
            print(f"  ❌ {r['invoice']}: {r['error']}")

    # Final assessment
    print("\n" + "="*60)
    print("ASSESSMENT")
    print("="*60)

    if successful_tests:
        if avg_accuracy >= 0.90:
            print("✅ EXCELLENT: Average accuracy meets 90% target (PRD requirement)")
        elif avg_accuracy >= 0.70:
            print("⚠️  ACCEPTABLE: Average accuracy meets 70% threshold (TRD-033)")
            print("   Recommendation: Improve prompt engineering to reach 90% target")
        else:
            print("❌ NEEDS IMPROVEMENT: Average accuracy below 70% threshold")
            print("   Recommendation: Review GPT-4o prompt and schema clarity")

        print(f"\nTarget Accuracy: 90% (PRD)")
        print(f"Threshold: 70% (TRD-033)")
        print(f"Achieved: {avg_accuracy:.1%}")
        print(f"Gap: {(0.90 - avg_accuracy) * 100:+.1f} percentage points to target")

    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
