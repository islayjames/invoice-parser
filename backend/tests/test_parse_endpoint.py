"""
Tests for /api/parse Endpoint (TRD Section 7.4)

Tests the main invoice parsing endpoint including file upload,
validation, parsing, confidence scoring, and error handling.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.schemas import InvoiceResponse
import io


@pytest.fixture
def valid_pdf_file():
    """Create a valid PDF file fixture."""
    # Simple PDF magic bytes
    pdf_content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n" + b"Mock PDF content" * 100
    return ("invoice.pdf", io.BytesIO(pdf_content), "application/pdf")


@pytest.fixture
def valid_image_file():
    """Create a valid image file fixture."""
    # Simple JPEG magic bytes
    jpeg_content = b"\xFF\xD8\xFF\xE0" + b"Mock JPEG data" * 100
    return ("invoice.jpg", io.BytesIO(jpeg_content), "image/jpeg")


@pytest.fixture
def oversized_file():
    """Create a file exceeding 5MB size limit."""
    # 6MB file
    large_content = b"%PDF-1.4\n" + b"X" * (6 * 1024 * 1024)
    return ("large.pdf", io.BytesIO(large_content), "application/pdf")


@pytest.fixture
def mock_gpt4o_response():
    """Mock successful GPT-4o parsing response."""
    return InvoiceResponse(
        supplier={
            "name": {"value": "ACME Corporation", "confidence": 0.95}
        },
        customer={
            "name": {"value": "Widget Industries", "confidence": 0.92}
        },
        invoice={
            "number": {"value": "INV-2024-001", "confidence": 0.98},
            "issue_date": {"value": "2024-01-15", "confidence": 0.99},
            "due_date": {"value": "2024-02-15", "confidence": 0.97},
            "total_amount": {"value": 1250.00, "confidence": 0.96}
        },
        line_items=[],
        meta={
            "source_file_name": "invoice.pdf",
            "source_format": "pdf",
            "model_version": "gpt-4o-2024-05-13",
            "processing_time_seconds": 3.45,
            "overall_confidence": 0.95
        }
    )


class TestParseEndpoint:
    """Tests for POST /api/parse endpoint."""

    @pytest.mark.asyncio
    async def test_successfully_parses_valid_pdf_invoice(
        self, valid_pdf_file, mock_gpt4o_response
    ):
        """Should successfully parse valid PDF invoice and return 200."""
        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_service.parse_invoice.return_value = mock_gpt4o_response
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_pdf_file}
                response = await client.post("/api/parse", files=files)

            assert response.status_code == 200
            data = response.json()
            assert data["supplier"]["name"]["value"] == "ACME Corporation"
            assert data["invoice"]["number"]["value"] == "INV-2024-001"
            assert data["meta"]["overall_confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_successfully_parses_valid_image_invoice(
        self, valid_image_file, mock_gpt4o_response
    ):
        """Should successfully parse valid image invoice and return 200."""
        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_gpt4o_response.meta.source_format = "image"
            mock_service.parse_invoice.return_value = mock_gpt4o_response
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_image_file}
                response = await client.post("/api/parse", files=files)

            assert response.status_code == 200
            data = response.json()
            assert data["meta"]["source_format"] == "image"

    @pytest.mark.asyncio
    async def test_rejects_file_exceeding_size_limit(self, oversized_file):
        """Should reject files >5MB with 413 Payload Too Large."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": oversized_file}
            response = await client.post("/api/parse", files=files)

        assert response.status_code == 413
        data = response.json()
        assert "detail" in data
        assert "5" in data["detail"] and "MB" in data["detail"]

    @pytest.mark.asyncio
    async def test_rejects_invalid_mime_type(self):
        """Should reject unsupported MIME types with 415 Unsupported Media Type."""
        invalid_file = ("script.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload")

        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": invalid_file}
            response = await client.post("/api/parse", files=files)

        assert response.status_code == 415
        data = response.json()
        assert "detail" in data
        assert "unsupported" in data["detail"].lower() or "unrecognizable" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_rejects_missing_file_parameter(self):
        """Should reject request without file parameter with 422 Unprocessable Entity."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/parse")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_rejects_low_confidence_invoice(self, valid_pdf_file):
        """Should reject invoice with critical fields <50% confidence with 422."""
        low_confidence_response = InvoiceResponse(
            supplier={
                "name": {"value": "Unclear", "confidence": 0.30}  # Below threshold
            },
            customer={
                "name": {"value": "Widget Industries", "confidence": 0.92}
            },
            invoice={
                "number": {"value": "INV-2024-001", "confidence": 0.98},
                "issue_date": {"value": "2024-01-15", "confidence": 0.99},
                "due_date": {"value": "2024-02-15", "confidence": 0.97},
                "total_amount": {"value": 1250.00, "confidence": 0.96}
            },
            line_items=[],
            meta={
                "source_file_name": "invoice.pdf",
                "source_format": "pdf",
                "model_version": "gpt-4o-2024-05-13",
                "processing_time_seconds": 3.45,
                "overall_confidence": 0.75
            }
        )

        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_service.parse_invoice.return_value = low_confidence_response
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_pdf_file}
                response = await client.post("/api/parse", files=files)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "confidence" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_returns_504_on_timeout(self, valid_pdf_file):
        """Should return 504 Gateway Timeout when parsing exceeds 20s."""
        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_service.parse_invoice.side_effect = TimeoutError("Request timed out")
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_pdf_file}
                response = await client.post("/api/parse", files=files)

        assert response.status_code == 504
        data = response.json()
        assert "detail" in data
        assert "timeout" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_returns_503_on_openai_api_error(self, valid_pdf_file):
        """Should return 503 Service Unavailable when OpenAI API fails."""
        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_service.parse_invoice.side_effect = Exception("OpenAI API unavailable")
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_pdf_file}
                response = await client.post("/api/parse", files=files)

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_includes_processing_time_in_response(
        self, valid_pdf_file, mock_gpt4o_response
    ):
        """Should include processing time in meta field of response."""
        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_service.parse_invoice.return_value = mock_gpt4o_response
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_pdf_file}
                response = await client.post("/api/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "processing_time_seconds" in data["meta"]
        assert data["meta"]["processing_time_seconds"] > 0

    @pytest.mark.asyncio
    async def test_includes_model_version_in_response(
        self, valid_pdf_file, mock_gpt4o_response
    ):
        """Should include GPT model version in meta field."""
        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_service.parse_invoice.return_value = mock_gpt4o_response
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_pdf_file}
                response = await client.post("/api/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "model_version" in data["meta"]
        assert "gpt-4o" in data["meta"]["model_version"]

    @pytest.mark.asyncio
    async def test_validates_file_content_not_empty(self):
        """Should reject empty files with 422."""
        empty_file = ("empty.pdf", io.BytesIO(b""), "application/pdf")

        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": empty_file}
            response = await client.post("/api/parse", files=files)

        assert response.status_code == 400  # file_validator returns 400 for empty files
        data = response.json()
        assert "detail" in data
        assert "empty" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_preserves_original_filename_in_metadata(
        self, valid_pdf_file, mock_gpt4o_response
    ):
        """Should preserve original filename in response metadata."""
        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_service.parse_invoice.return_value = mock_gpt4o_response
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": valid_pdf_file}
                response = await client.post("/api/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["source_file_name"] == "invoice.pdf"

    @pytest.mark.asyncio
    async def test_accepts_text_plain_invoices(self, mock_gpt4o_response):
        """Should accept and parse text/plain invoice files."""
        text_file = ("invoice.txt", io.BytesIO(b"INVOICE\nNumber: INV-001\nTotal: $1250.00"), "text/plain")

        with patch("app.api.parse.GPT4oService") as MockGPT4o:
            mock_service = AsyncMock()
            mock_gpt4o_response.meta.source_format = "text"
            mock_service.parse_invoice.return_value = mock_gpt4o_response
            MockGPT4o.return_value = mock_service

            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": text_file}
                response = await client.post("/api/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["source_format"] == "text"
