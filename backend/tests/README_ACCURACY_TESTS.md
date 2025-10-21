# Accuracy Validation Tests (TRD-033)

## Overview

Real API accuracy validation tests that call GPT-4o with actual invoices and compare extracted fields to ground truth.

**No mocking** - These tests validate end-to-end extraction accuracy with real OpenAI API calls.

---

## Quick Start

```bash
# Run accuracy test with detailed report
pytest tests/test_accuracy_validation.py::test_single_invoice_accuracy -v -s

# Run all accuracy tests
pytest tests/test_accuracy_validation.py -v -s

# Skip expensive API tests in CI
pytest -m "not real_api"
```

---

## Test Files

### `test_accuracy_validation.py`

Contains two main tests:

1. **`test_single_invoice_accuracy()`**
   - Loads `1Password-invoice-2025-10-05.pdf` (46KB sample)
   - Calls real GPT-4o API
   - Compares 14 expected fields to ground truth
   - Generates detailed console report
   - Asserts accuracy ≥70%

2. **`test_line_items_accuracy()`**
   - Validates line item extraction
   - Checks count and field accuracy
   - Compares description, quantity, unit_price, total

---

## Test Output Example

```
============================================================
ACCURACY VALIDATION REPORT
============================================================
Invoice: 1Password-invoice-2025-10-05.pdf
Accuracy: 85.7% (12/14 fields)

Field Comparison:
------------------------------------------------------------
  ✓ supplier.name                AgileBits Inc. dba 1Password == AgileBits Inc. dba 1Password
  ✓ invoice.number               in_1SEvjvHBax7L5HDfxS6QV4EE == in_1SEvjvHBax7L5HDfxS6QV4EE
  ✓ invoice.total                3.99 == 3.99
  ✗ customer.account_id          (missing) != (missing)
  ...
============================================================

✅ Accuracy test PASSED: 85.7% >= 70.0%
```

---

## Key Features

### Flexible Field Matching

- **Empty strings treated as missing**: `"" == None`
- **Float tolerance**: Numbers match within 0.01
- **Case insensitive**: String comparison ignores case
- **Type conversion**: `"3.99"` matches `3.99`

### Ground Truth Format

```json
{
  "file_name": "1Password-invoice-2025-10-05.pdf",
  "expected_fields": {
    "supplier.name": "AgileBits Inc. dba 1Password",
    "invoice.number": "in_1SEvjvHBax7L5HDfxS6QV4EE",
    "invoice.total": 3.99,
    ...
  },
  "expected_line_items": [...]
}
```

### Test Markers

```python
@pytest.mark.real_api  # Skip with: pytest -m "not real_api"
@pytest.mark.asyncio   # Async test support
```

---

## Configuration

### Accuracy Threshold

```python
ACCURACY_THRESHOLD = 0.70  # 70% minimum
```

Flexible for demo purposes. Can be raised to 0.90 (90%) for production.

### Test Invoice

```python
TEST_INVOICE_FILE = "1Password-invoice-2025-10-05.pdf"
```

- **Size**: 46KB (smallest sample)
- **Complexity**: Simple subscription invoice
- **Ground Truth**: 14 fields + 1 line item

---

## Extending Tests

### Test Multiple Invoices

```python
@pytest.mark.parametrize("invoice_name", [
    "1Password-invoice-2025-10-05.pdf",
    "Atlassian_Invoice_IN-003-942-505.pdf",
    "Jell-2024-02-03.pdf",
])
async def test_invoice_accuracy(invoice_name):
    pdf_bytes, ground_truth = load_test_data(invoice_name)
    # ... same test logic
```

### Generate CSV Report

```python
import csv

def save_accuracy_report_csv(results, output_path="accuracy_report.csv"):
    with open(output_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Field", "Matched", "Extracted", "Expected"])
        for field, matched, extracted, expected in results:
            writer.writerow([field, matched, extracted, expected])
```

---

## CI/CD Integration

### Skip Expensive Tests in CI

```yaml
# .github/workflows/test.yml
- name: Run tests (skip real API)
  run: pytest -m "not real_api"
```

### Run Nightly Accuracy Tests

```yaml
# .github/workflows/nightly-accuracy.yml
- name: Run accuracy validation
  run: pytest -m "real_api" -v -s
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## TRD References

- **TRD-033**: Accuracy Validation Against Test Dataset
- **Section 11**: Testing & Validation Strategy
- **NFR-001**: Parse time ≤20s
- **NFR-005**: Field extraction accuracy ≥90%

---

**Created**: 2025-10-20
**Test Runner**: test-runner sub-agent
