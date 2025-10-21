"""
Configuration management for invoice parser API (TRD Section 10.3)

Loads and validates application settings from environment variables using Pydantic.
Supports both .env file loading and direct environment variable access.

Configuration priorities (highest to lowest):
1. Explicitly set environment variables
2. Values from .env file
3. Default values defined in Settings class

Example .env file:
    OPENAI_API_KEY=sk-...
    OPENAI_MODEL=gpt-4o-2024-08-06
    CORS_ORIGINS=http://localhost:3000,https://app.example.com
    LOG_LEVEL=DEBUG
    MAX_FILE_SIZE_MB=10
    MAX_PARSE_TIME_SECONDS=30
    ALLOWED_FILE_TYPES=application/pdf,image/jpeg,image/png

Usage:
    from app.config import get_settings

    settings = get_settings()
    print(settings.openai_model)  # "gpt-4o-2024-08-06"
    print(settings.max_file_size_mb)  # 5
"""

from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import Field, field_validator, model_validator
from typing import List, Union, Tuple, Type
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    All settings can be configured via environment variables or a .env file.
    String fields are automatically stripped of leading/trailing whitespace.
    Comma-separated strings are automatically parsed into lists.

    Attributes:
        openai_api_key: OpenAI API key for GPT-4o access (required)
        openai_model: OpenAI model version to use (default: gpt-4o-2024-08-06)
        cors_origins: Allowed CORS origins, comma-separated or list (default: localhost:3000)
        log_level: Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL, default: INFO)
        max_file_size_mb: Maximum allowed file upload size in MB (default: 5, must be > 0)
        max_parse_time_seconds: Maximum allowed parsing time in seconds (default: 20, must be > 0)
        allowed_file_types: Allowed MIME types, comma-separated or list (default: common document formats)

    Environment Variable Examples:
        OPENAI_API_KEY=sk-proj-abcd1234...
        OPENAI_MODEL=gpt-4o-2024-08-06
        CORS_ORIGINS=http://localhost:3000,https://app.example.com
        LOG_LEVEL=DEBUG
        MAX_FILE_SIZE_MB=10
        MAX_PARSE_TIME_SECONDS=30
        ALLOWED_FILE_TYPES=application/pdf,image/jpeg,image/png
    """

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file if present
        case_sensitive=False,  # Environment variables are case-insensitive
        env_prefix="",  # No prefix required (e.g., use OPENAI_API_KEY not APP_OPENAI_API_KEY)
        extra='ignore',  # Ignore extra environment variables not defined in Settings
        str_strip_whitespace=True  # Automatically strip whitespace from string values
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        min_length=1,
        description="OpenAI API key (required, must not be empty)"
    )
    openai_model: str = Field(
        default="gpt-4o-2024-08-06",
        description="OpenAI model version for invoice extraction"
    )
    openai_temperature: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="GPT model temperature for response consistency (0.0-1.0)"
    )
    openai_max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum response tokens for GPT model"
    )
    openai_timeout: float = Field(
        default=20.0,
        gt=0.0,
        description="OpenAI API request timeout in seconds"
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Application environment (development/staging/production)"
    )

    # CORS Configuration
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000",
        description="Allowed CORS origins (comma-separated string or list)"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)"
    )

    # Processing Limits (TRD Section 6.2 - Non-Functional Requirements)
    max_file_size_mb: int = Field(
        default=5,
        gt=0,
        description="Maximum file upload size in megabytes (must be > 0)"
    )
    max_parse_time_seconds: int = Field(
        default=20,
        gt=0,
        description="Maximum parsing time in seconds (must be > 0)"
    )

    # File Type Validation (TRD Section 6.3 - Security)
    allowed_file_types: Union[str, List[str]] = Field(
        default="application/pdf,image/jpeg,image/png,image/tiff,image/bmp,image/webp,image/heic,image/heif,image/gif,text/plain,text/markdown",
        description="Allowed file MIME types (comma-separated string or list)"
    )

    @model_validator(mode='after')
    def parse_list_fields(self):
        """
        Parse comma-separated string fields into lists.

        Automatically converts cors_origins and allowed_file_types from
        comma-separated strings to lists if they were provided as strings.
        This allows flexible configuration via environment variables:

        Examples:
            CORS_ORIGINS=http://localhost:3000
            CORS_ORIGINS=http://localhost:3000,https://app.example.com

            Both formats are supported and normalized to lists internally.

        Returns:
            self: The Settings instance with parsed list fields
        """
        # Parse CORS origins from comma-separated string
        if isinstance(self.cors_origins, str):
            self.cors_origins = [origin.strip() for origin in self.cors_origins.split(',')]

        # Parse allowed file types from comma-separated string
        if isinstance(self.allowed_file_types, str):
            self.allowed_file_types = [ft.strip() for ft in self.allowed_file_types.split(',')]

        return self

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """
        Validate and normalize log level to uppercase.

        Ensures the log level is one of the standard Python logging levels.
        Invalid levels are silently defaulted to INFO to prevent application
        startup failures due to misconfiguration.

        Args:
            v: The log level value from environment variable or default

        Returns:
            str: Uppercase log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)

        Examples:
            validate_log_level("debug") -> "DEBUG"
            validate_log_level("info") -> "INFO"
            validate_log_level("invalid") -> "INFO" (fallback)
        """
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            # Fallback to INFO for invalid log levels to prevent startup failure
            return 'INFO'
        return v.upper()


@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings singleton instance.

    Uses functools.lru_cache to ensure only one Settings instance is created
    and reused throughout the application lifecycle. This improves performance
    and ensures consistent configuration across all modules.

    The singleton pattern is important because:
    1. Environment variable parsing happens only once
    2. Validation happens only once at startup
    3. All modules see the same configuration

    Returns:
        Settings: The singleton Settings instance with validated configuration

    Example:
        from app.config import get_settings

        settings = get_settings()
        api_key = settings.openai_api_key
        max_size = settings.max_file_size_mb

        # Second call returns the same instance (no re-parsing)
        settings2 = get_settings()
        assert settings is settings2  # True

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    return Settings()
