"""
Pytest configuration and fixtures for Invoice Parser tests
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path


@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    from main import app
    return TestClient(app)


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory"""
    return Path(__file__).parent.parent.parent / "tests" / "fixtures" / "invoices"


@pytest.fixture
def sample_invoice_pdf(fixtures_dir):
    """Load sample PDF invoice for testing"""
    # Placeholder - will be populated in TRD-006
    pass


@pytest.fixture
def test_dataset(fixtures_dir):
    """Load complete test dataset with ground truth"""
    # Placeholder - will be populated in TRD-006
    pass
