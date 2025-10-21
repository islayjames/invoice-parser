# Invoice Test Dataset

This directory contains test invoice samples and their corresponding ground truth data for accuracy validation.

## Dataset Structure

```
tests/fixtures/invoices/
├── README.md                           # This file
├── sample-001.pdf                      # Sample invoice 1
├── sample-001-ground-truth.json        # Ground truth for sample 1
├── sample-002.pdf                      # Sample invoice 2
├── sample-002-ground-truth.json        # Ground truth for sample 2
... (total 10-20 samples)
```

## Dataset Requirements

### Quantity
- **Minimum**: 10 PDF invoice samples
- **Target**: 15-20 PDF invoice samples
- **Maximum**: 20 samples (for manageable testing)

### Quality Criteria
- **Format**: Clean, typed text PDFs (not scanned/handwritten)
- **Language**: Primarily English
- **Layouts**: Diverse vendor formats (service invoices, product invoices, mixed)
- **Vendors**: Different templates to test generalization
- **File Size**: Each file ≤5MB

### Sample Categories
1. **Service Invoices** (4-6 samples): Consulting, professional services, subscriptions
2. **Product Invoices** (4-6 samples): Physical goods with itemized SKUs
3. **Mixed Invoices** (4-6 samples): Combination of services and products
4. **Edge Cases** (2-4 samples): Multiple currencies, high line item counts, multi-page

## Ground Truth Format

Each PDF invoice must have a corresponding `-ground-truth.json` file with manually verified fields.

### Ground Truth JSON Schema

```json
{
  "file_name": "sample-001.pdf",
  "description": "Service invoice from consulting firm",
  "expected_fields": {
    "supplier.name": "Acme Consulting Corp",
    "supplier.address": "123 Main Street, City, State 12345",
    "supplier.tax_id": "12-3456789",
    "customer.name": "Client Company Inc",
    "customer.address": "456 Oak Avenue, Town, State 67890",
    "invoice.number": "INV-2025-001",
    "invoice.issue_date": "2025-01-15",
    "invoice.due_date": "2025-02-15",
    "invoice.currency": "USD",
    "invoice.subtotal": 1000.00,
    "invoice.tax": 80.00,
    "invoice.total": 1080.00,
    "invoice.payment_terms": "Net 30",
    "invoice.po_number": "PO-2025-100"
  },
  "expected_line_items_count": 1,
  "expected_line_items": [
    {
      "description": "Professional Consulting Services",
      "quantity": 10,
      "unit_price": 100.00,
      "total": 1000.00
    }
  ],
  "notes": "Clean invoice with standard layout, all fields clearly visible"
}
```

### Field Accuracy Validation

Ground truth is used to calculate field extraction accuracy:

```python
accuracy = (correctly_extracted_fields / total_expected_fields) * 100
```

**Success Criteria**: ≥90% accuracy across all samples

## Dataset Creation Process

### Step 1: Collect PDF Samples

**Sources:**
- Public invoice templates (free downloads)
- Generated from invoicing software (QuickBooks, FreshBooks, Wave)
- Stock invoice PDFs (InvoiceLion, Invoice-Generator.com)
- Real invoices with sensitive data redacted

**Important:** Ensure invoices contain no real sensitive information (redact or use templates)

### Step 2: Manual Verification

For each PDF:
1. Open invoice in PDF viewer
2. Manually extract all visible fields
3. Create ground truth JSON file
4. Double-check all values for accuracy
5. Document any special characteristics in `notes` field

### Step 3: Validation

Run validation script to ensure dataset quality:

```bash
cd /home/james/dev/invoice-parser/tests/fixtures/invoices
python validate_dataset.py
```

Expected output:
- ✅ All PDFs present and readable
- ✅ All ground truth files valid JSON
- ✅ File sizes ≤5MB
- ✅ All required fields present in ground truth

## Sample Ground Truth Template

Copy this template for each new sample:

```json
{
  "file_name": "sample-XXX.pdf",
  "description": "Brief description of invoice type and layout",
  "expected_fields": {
    "supplier.name": "",
    "supplier.address": "",
    "supplier.phone": "",
    "supplier.email": "",
    "supplier.tax_id": "",
    "customer.name": "",
    "customer.address": "",
    "customer.account_id": "",
    "invoice.number": "",
    "invoice.issue_date": "YYYY-MM-DD",
    "invoice.due_date": "YYYY-MM-DD",
    "invoice.currency": "USD",
    "invoice.subtotal": 0.00,
    "invoice.tax": 0.00,
    "invoice.total": 0.00,
    "invoice.payment_terms": "",
    "invoice.po_number": ""
  },
  "expected_line_items_count": 0,
  "expected_line_items": [],
  "notes": ""
}
```

## Usage in Tests

The test dataset is used in:

### Backend Integration Tests
```python
@pytest.mark.integration
def test_accuracy_validation(test_dataset):
    """Test field extraction accuracy against ground truth"""
    results = []
    for sample in test_dataset:
        parsed = parse_invoice(sample["pdf_path"])
        accuracy = calculate_accuracy(parsed, sample["ground_truth"])
        results.append(accuracy)

    avg_accuracy = sum(results) / len(results)
    assert avg_accuracy >= 0.90  # 90% accuracy threshold
```

### Performance Tests
```python
@pytest.mark.slow
def test_parse_time_under_20s(test_dataset):
    """Verify parsing completes in ≤20 seconds"""
    for sample in test_dataset:
        start = time.time()
        parse_invoice(sample["pdf_path"])
        duration = time.time() - start
        assert duration <= 20.0
```

## Current Status

**Dataset Completion**: 0/10 minimum samples

**Next Steps:**
1. Collect 10-20 clean PDF invoice samples
2. Create ground truth JSON for each sample
3. Validate dataset with validation script
4. Run accuracy tests to verify ≥90% extraction rate

**Estimated Time**: 4 hours
- PDF collection: 1 hour
- Ground truth creation: 2-3 hours (15-20 min per invoice)
- Validation and testing: 1 hour

## Notes

- This is a **critical blocker** for accuracy validation (TRD-033)
- Dataset must be completed before Sprint 4 (Testing & Quality)
- Consider automating ground truth extraction with GPT-4o and manual verification
- Keep dataset diverse to ensure robust testing
- Document any edge cases or difficult invoices for future improvement
