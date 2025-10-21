"""
Tests for Confidence Scorer Service (TRD Section 7.3)

Tests confidence-based validation and rejection logic for invoice parsing.
All critical fields must have ≥50% confidence to pass validation.
"""

import pytest
from app.services.confidence_scorer import validate_confidence


class TestConfidenceValidation:
    """Tests for validate_confidence function."""

    def test_accepts_invoice_with_all_high_confidence_scores(self):
        """Should accept invoice when all critical fields have ≥90% confidence."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.95}
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.92}
            },
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.98},
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97},
                "total_amount": {"value": 1250.00, "confidence": 0.96}
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        assert is_valid is True
        assert error_msg is None
        assert overall_score >= 0.90

    def test_rejects_invoice_with_low_confidence_supplier_name(self):
        """Should reject invoice when supplier.name confidence <50%."""
        invoice_data = {
            "supplier": {
                "name": {"value": "Unclear Name", "confidence": 0.45}  # Below threshold
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.92}
            },
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.98},
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97},
                "total_amount": {"value": 1250.00, "confidence": 0.96}
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        assert is_valid is False
        assert error_msg is not None
        assert "supplier.name" in error_msg.lower()
        assert "critical field" in error_msg.lower() or "confidence" in error_msg.lower()

    def test_rejects_invoice_with_low_confidence_invoice_number(self):
        """Should reject invoice when invoice.number confidence <50%."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.95}
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.92}
            },
            "invoice": {
                "number": {"value": "unclear", "confidence": 0.35},  # Below threshold
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97},
                "total_amount": {"value": 1250.00, "confidence": 0.96}
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        assert is_valid is False
        assert error_msg is not None
        assert "invoice.number" in error_msg.lower()

    def test_rejects_invoice_with_low_confidence_total_amount(self):
        """Should reject invoice when invoice.total_amount confidence <50%."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.95}
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.92}
            },
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.98},
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97},
                "total_amount": {"value": 1250.00, "confidence": 0.40}  # Below threshold
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        assert is_valid is False
        assert error_msg is not None
        assert "total_amount" in error_msg.lower()

    def test_accepts_invoice_with_moderate_confidence_scores(self):
        """Should accept invoice when all critical fields are exactly at 50% threshold."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.50}  # Exactly at threshold
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.50}
            },
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.50},
                "issue_date": {"value": "2024-01-15", "confidence": 0.50},
                "due_date": {"value": "2024-02-15", "confidence": 0.50},
                "total_amount": {"value": 1250.00, "confidence": 0.50}
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        assert is_valid is True
        assert error_msg is None
        assert overall_score == 0.50

    def test_warns_on_moderate_confidence_ranges(self):
        """Should pass but log warnings for fields with 50-90% confidence."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.75}  # Warning range
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.85}
            },
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.65},  # Warning range
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97},
                "total_amount": {"value": 1250.00, "confidence": 0.96}
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        # Should still be valid despite warnings
        assert is_valid is True
        assert error_msg is None
        # Overall score should be average of all scores
        assert 0.70 <= overall_score <= 0.90

    def test_handles_missing_critical_fields(self):
        """Should reject invoice when critical fields are missing."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.95}
            },
            # Missing customer.name (critical field)
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.98},
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97}
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        assert is_valid is False
        assert error_msg is not None
        assert "missing" in error_msg.lower() or "required" in error_msg.lower()

    def test_ignores_optional_fields_with_low_confidence(self):
        """Should accept invoice even if optional fields have low confidence."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.95},
                "phone": {"value": "unclear", "confidence": 0.20}  # Optional field, low confidence
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.92}
            },
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.98},
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97},
                "total_amount": {"value": 1250.00, "confidence": 0.96},
                "po_number": {"value": "guess", "confidence": 0.10}  # Optional, low confidence
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        # Should be valid - optional fields don't affect critical validation
        assert is_valid is True
        assert error_msg is None

    def test_calculates_overall_confidence_correctly(self):
        """Should calculate overall confidence as average of all field scores."""
        invoice_data = {
            "supplier": {
                "name": {"value": "ACME Corp", "confidence": 0.90}
            },
            "customer": {
                "name": {"value": "Widget Inc", "confidence": 0.80}
            },
            "invoice": {
                "number": {"value": "INV-001", "confidence": 0.70},
                "issue_date": {"value": "2024-01-15", "confidence": 1.00},
                "due_date": {"value": "2024-02-15", "confidence": 1.00},
                "total_amount": {"value": 1250.00, "confidence": 0.60}
            }
        }

        is_valid, error_msg, overall_score = validate_confidence(invoice_data)

        # Average: (0.90 + 0.80 + 0.70 + 1.00 + 1.00 + 0.60) / 6 = 0.833...
        assert is_valid is True
        assert 0.83 <= overall_score <= 0.84
