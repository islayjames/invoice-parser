"""
Test suite for configuration management (TRD-008)

RED Phase: These tests are expected to FAIL because the config module
has not been implemented yet. This is intentional in TDD.

Tests cover:
- Loading OpenAI API key from environment
- Validation when API key is missing
- Loading CORS origins configuration
- Loading application settings (LOG_LEVEL, MAX_FILE_SIZE_MB, etc.)
"""

import pytest
import os
from unittest.mock import patch

# This import will fail in RED phase - that's expected!
from app.config import Settings, get_settings


class TestConfigLoading:
    """Test configuration loading from environment variables."""

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key-12345',
        'CORS_ORIGINS': 'http://localhost:3000,https://example.com',
        'LOG_LEVEL': 'DEBUG',
        'MAX_FILE_SIZE_MB': '10'
    })
    def test_loads_openai_api_key_from_env(self):
        """Should load OPENAI_API_KEY from environment variables."""
        settings = Settings()

        assert settings.openai_api_key == 'sk-test-key-12345'
        assert settings.openai_api_key.startswith('sk-')

    @patch.dict(os.environ, {}, clear=True)
    def test_raises_error_if_api_key_missing(self):
        """Should raise ValidationError when OPENAI_API_KEY is not set."""
        with pytest.raises(Exception) as exc_info:
            Settings()

        # Should mention the missing API key
        error_message = str(exc_info.value).lower()
        assert 'openai' in error_message or 'api' in error_message or 'key' in error_message

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key',
        'CORS_ORIGINS': 'http://localhost:3000,https://app.example.com,https://staging.example.com'
    })
    def test_loads_cors_origins(self):
        """Should parse CORS_ORIGINS into a list."""
        settings = Settings()

        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) == 3
        assert 'http://localhost:3000' in settings.cors_origins
        assert 'https://app.example.com' in settings.cors_origins
        assert 'https://staging.example.com' in settings.cors_origins

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key',
        'CORS_ORIGINS': 'http://localhost:3000',
        'LOG_LEVEL': 'INFO',
        'MAX_FILE_SIZE_MB': '5',
        'MAX_PARSE_TIME_SECONDS': '20',
        'ALLOWED_FILE_TYPES': 'application/pdf,image/png,image/jpeg,text/plain'
    })
    def test_loads_application_settings(self):
        """Should load all application settings from environment."""
        settings = Settings()

        # Logging configuration
        assert settings.log_level == 'INFO'

        # File validation settings (from TRD Section 5.2.1)
        assert settings.max_file_size_mb == 5
        assert settings.max_parse_time_seconds == 20

        # Allowed file types
        assert isinstance(settings.allowed_file_types, list)
        assert 'application/pdf' in settings.allowed_file_types
        assert 'image/png' in settings.allowed_file_types
        assert 'image/jpeg' in settings.allowed_file_types
        assert 'text/plain' in settings.allowed_file_types


class TestConfigDefaults:
    """Test default configuration values."""

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key'
    }, clear=True)
    def test_uses_default_values_when_not_specified(self):
        """Should use default values when environment variables are not set."""
        settings = Settings()

        # Default LOG_LEVEL should be 'INFO' per TRD
        assert settings.log_level == 'INFO'

        # Default MAX_FILE_SIZE_MB should be 5 per TRD Section 4.1
        assert settings.max_file_size_mb == 5

        # Default MAX_PARSE_TIME_SECONDS should be 20 per NFR-001
        assert settings.max_parse_time_seconds == 20

        # Default CORS_ORIGINS should include localhost for development
        assert isinstance(settings.cors_origins, list)
        assert 'http://localhost:3000' in settings.cors_origins

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key',
        'OPENAI_MODEL': 'gpt-4o-custom'
    })
    def test_allows_custom_openai_model(self):
        """Should allow custom OpenAI model override."""
        settings = Settings()

        assert settings.openai_model == 'gpt-4o-custom'

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key'
    }, clear=True)
    def test_default_openai_model(self):
        """Should default to gpt-4o-2024-08-06 per TRD Section 3.2."""
        settings = Settings()

        assert settings.openai_model == 'gpt-4o-2024-08-06'


class TestGetSettings:
    """Test get_settings() singleton pattern."""

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key-singleton'
    })
    def test_get_settings_returns_singleton(self):
        """get_settings() should return the same instance (singleton pattern)."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same object instance
        assert settings1 is settings2
        assert id(settings1) == id(settings2)

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key-dependency'
    })
    def test_get_settings_for_dependency_injection(self):
        """get_settings() should be usable for FastAPI dependency injection."""
        settings = get_settings()

        assert settings is not None
        assert hasattr(settings, 'openai_api_key')
        assert hasattr(settings, 'cors_origins')
        assert hasattr(settings, 'log_level')


class TestConfigValidation:
    """Test configuration validation rules."""

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key',
        'MAX_FILE_SIZE_MB': '-5'  # Invalid negative value
    })
    def test_rejects_negative_file_size(self):
        """Should reject negative MAX_FILE_SIZE_MB."""
        with pytest.raises(Exception):
            Settings()

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key',
        'MAX_PARSE_TIME_SECONDS': '0'  # Invalid zero value
    })
    def test_rejects_zero_parse_time(self):
        """Should reject zero or negative MAX_PARSE_TIME_SECONDS."""
        with pytest.raises(Exception):
            Settings()

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key',
        'LOG_LEVEL': 'INVALID_LEVEL'
    })
    def test_validates_log_level(self):
        """Should validate LOG_LEVEL against allowed values."""
        # Should either reject or default to valid level
        settings = Settings()
        assert settings.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
