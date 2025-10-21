"""
Configuration management for invoice parser API (TRD Section 10.3)

Loads settings from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import Field, field_validator, model_validator
from typing import List, Union, Tuple, Type
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="",
        extra='ignore',
        str_strip_whitespace=True
    )

    openai_api_key: str = Field(..., min_length=1)
    openai_model: str = "gpt-4o-2024-08-06"

    cors_origins: Union[str, List[str]] = "http://localhost:3000"

    log_level: str = "INFO"

    max_file_size_mb: int = Field(default=5, gt=0)
    max_parse_time_seconds: int = Field(default=20, gt=0)

    allowed_file_types: Union[str, List[str]] = "application/pdf,image/jpeg,image/png,image/tiff,image/bmp,image/webp,image/heic,image/heif,image/gif,text/plain,text/markdown"

    @model_validator(mode='after')
    def parse_list_fields(self):
        """Convert comma-separated strings to lists"""
        if isinstance(self.cors_origins, str):
            self.cors_origins = [origin.strip() for origin in self.cors_origins.split(',')]

        if isinstance(self.allowed_file_types, str):
            self.allowed_file_types = [ft.strip() for ft in self.allowed_file_types.split(',')]

        return self

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            return 'INFO'
        return v.upper()


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings singleton instance

    Uses lru_cache to ensure only one Settings instance is created
    """
    return Settings()
