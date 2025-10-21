"""
TDD RED Phase: File Validation Service Tests
Tests for MIME type, size, and extension validation per TRD Section 7.1

Expected to FAIL: Implementation doesn't exist yet
"""

import pytest
from io import BytesIO
from fastapi import UploadFile, HTTPException
from unittest.mock import Mock, AsyncMock

# This import will FAIL - implementation doesn't exist yet
from app.services.file_validator import validate_file


class TestFileValidation:
    """Test suite for file validation service"""

    # Fixtures for test data
    @pytest.fixture
    def valid_pdf_file(self):
        """Create a mock valid PDF file"""
        content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n" + b"x" * 1024  # 1KB PDF
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "invoice.pdf"
        upload_file.content_type = "application/pdf"
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    @pytest.fixture
    def valid_jpeg_file(self):
        """Create a mock valid JPEG file"""
        content = b"\xff\xd8\xff\xe0" + b"x" * 2048  # 2KB JPEG
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "invoice.jpg"
        upload_file.content_type = "image/jpeg"
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    @pytest.fixture
    def valid_png_file(self):
        """Create a mock valid PNG file"""
        content = b"\x89PNG\r\n\x1a\n" + b"x" * 1500  # 1.5KB PNG
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "invoice.png"
        upload_file.content_type = "image/png"
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    @pytest.fixture
    def valid_text_file(self):
        """Create a mock valid text file"""
        content = b"Invoice text content\n" * 100
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "invoice.txt"
        upload_file.content_type = "text/plain"
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    @pytest.fixture
    def oversized_file(self):
        """Create a file larger than 5MB"""
        content = b"x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "large_invoice.pdf"
        upload_file.content_type = "application/pdf"
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    @pytest.fixture
    def unsupported_mime_file(self):
        """Create a file with unsupported MIME type"""
        content = b"PK\x03\x04" + b"x" * 1024  # ZIP file signature
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "invoice.zip"
        upload_file.content_type = "application/zip"
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    @pytest.fixture
    def mime_spoofed_file(self):
        """Create a file with mismatched MIME type and content"""
        # Use better ZIP header that python-magic can detect
        # Standard minimal ZIP file header
        content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00test.txt" + b"\x00" * 100
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "invoice.pdf"  # PDF extension
        upload_file.content_type = "application/pdf"  # PDF MIME type
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    @pytest.fixture
    def empty_file(self):
        """Create an empty file"""
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "empty.pdf"
        upload_file.content_type = "application/pdf"
        upload_file.read = AsyncMock(return_value=b"")
        return upload_file

    @pytest.fixture
    def exact_5mb_file(self):
        """Create a file exactly 5MB in size"""
        content = b"x" * (5 * 1024 * 1024)  # Exactly 5MB
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "exactly_5mb.pdf"
        upload_file.content_type = "application/pdf"
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    # Test cases
    @pytest.mark.asyncio
    async def test_accepts_valid_pdf(self, valid_pdf_file):
        """Should accept valid PDF file within size limit"""
        result = await validate_file(valid_pdf_file)

        assert result is not None
        content, mime_type = result
        assert mime_type == "application/pdf"
        assert len(content) > 0
        assert content.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_accepts_valid_jpeg(self, valid_jpeg_file):
        """Should accept valid JPEG image file"""
        result = await validate_file(valid_jpeg_file)

        assert result is not None
        content, mime_type = result
        assert mime_type == "image/jpeg"
        assert len(content) > 0
        assert content.startswith(b"\xff\xd8\xff")

    @pytest.mark.asyncio
    async def test_accepts_valid_png(self, valid_png_file):
        """Should accept valid PNG image file"""
        result = await validate_file(valid_png_file)

        assert result is not None
        content, mime_type = result
        assert mime_type == "image/png"
        assert len(content) > 0
        assert content.startswith(b"\x89PNG")

    @pytest.mark.asyncio
    async def test_accepts_text_files(self, valid_text_file):
        """Should accept plain text files"""
        result = await validate_file(valid_text_file)

        assert result is not None
        content, mime_type = result
        assert mime_type == "text/plain"
        assert len(content) > 0
        assert b"Invoice" in content

    @pytest.mark.asyncio
    async def test_rejects_oversized_file(self, oversized_file):
        """Should reject file larger than 5MB with HTTP 413"""
        with pytest.raises(HTTPException) as exc_info:
            await validate_file(oversized_file)

        assert exc_info.value.status_code == 413
        assert "5MB" in str(exc_info.value.detail) or "size" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_rejects_unsupported_mime_type(self, unsupported_mime_file):
        """Should reject unsupported MIME type with HTTP 415"""
        with pytest.raises(HTTPException) as exc_info:
            await validate_file(unsupported_mime_file)

        assert exc_info.value.status_code == 415
        assert "unsupported" in str(exc_info.value.detail).lower() or "mime" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_rejects_mime_type_spoofing(self, mime_spoofed_file):
        """Should detect and reject MIME type spoofing (ZIP as PDF)"""
        # This test expects the validator to check magic bytes
        with pytest.raises(HTTPException) as exc_info:
            await validate_file(mime_spoofed_file)

        assert exc_info.value.status_code == 415
        # Should reject ZIP file even when declared as PDF
        assert ("mismatch" in str(exc_info.value.detail).lower() or
                "unsupported" in str(exc_info.value.detail).lower() or
                "invalid" in str(exc_info.value.detail).lower())

    @pytest.mark.asyncio
    async def test_validates_empty_file(self, empty_file):
        """Should handle empty file (0 bytes)"""
        with pytest.raises(HTTPException) as exc_info:
            await validate_file(empty_file)

        assert exc_info.value.status_code == 400
        assert "empty" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_validates_exact_5mb_file(self, exact_5mb_file):
        """Should accept file exactly at 5MB boundary"""
        result = await validate_file(exact_5mb_file)

        assert result is not None
        content, mime_type = result
        assert mime_type == "application/pdf"
        assert len(content) == 5 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_returns_file_content_and_mime(self, valid_pdf_file):
        """Should return tuple of (content: bytes, mime_type: str)"""
        result = await validate_file(valid_pdf_file)

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, mime_type = result
        assert isinstance(content, bytes)
        assert isinstance(mime_type, str)

    @pytest.mark.asyncio
    async def test_async_file_validation(self, valid_pdf_file):
        """Should support async/await pattern"""
        # Test that validate_file is properly async
        import asyncio

        result = await validate_file(valid_pdf_file)
        assert result is not None

    @pytest.mark.asyncio
    async def test_accepts_all_supported_image_formats(self):
        """Should accept all supported image MIME types"""
        supported_images = [
            ("image/jpeg", b"\xff\xd8\xff\xe0"),
            ("image/png", b"\x89PNG\r\n\x1a\n"),
            ("image/tiff", b"II*\x00"),
            ("image/bmp", b"BM"),
            ("image/webp", b"RIFF"),
            ("image/heic", b"\x00\x00\x00"),  # Simplified
            ("image/gif", b"GIF89a"),
        ]

        for mime_type, magic_bytes in supported_images:
            content = magic_bytes + b"x" * 1024
            upload_file = Mock(spec=UploadFile)
            upload_file.filename = f"test.{mime_type.split('/')[1]}"
            upload_file.content_type = mime_type
            upload_file.read = AsyncMock(return_value=content)

            result = await validate_file(upload_file)
            assert result is not None
            _, returned_mime = result
            assert returned_mime == mime_type

    @pytest.mark.asyncio
    async def test_accepts_markdown_files(self):
        """Should accept markdown text files"""
        content = b"# Invoice\n\n**Total**: $1000"
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "invoice.md"
        upload_file.content_type = "text/markdown"
        upload_file.read = AsyncMock(return_value=content)

        result = await validate_file(upload_file)
        assert result is not None
        returned_content, mime_type = result
        assert mime_type == "text/markdown"
        assert b"Invoice" in returned_content
