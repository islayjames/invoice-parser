"""
Structured logging configuration for Invoice Parser
Metadata-only logging (no invoice content) per NFR-004 privacy requirements
"""

import logging
import sys
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured logging
    Outputs JSON-like structured logs with metadata only
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured metadata"""
        # Base log entry
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present (from extra={} in log calls)
        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Format as key=value pairs for readability
        formatted_parts = []
        for key, value in log_data.items():
            if isinstance(value, str):
                formatted_parts.append(f'{key}="{value}"')
            else:
                formatted_parts.append(f'{key}={value}')

        return " ".join(formatted_parts)


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging with structured format

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    # Set structured formatter
    formatter = StructuredFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for module

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_with_metadata(
    logger: logging.Logger,
    level: str,
    message: str,
    **metadata: Any
) -> None:
    """
    Log message with structured metadata

    IMPORTANT: Never log invoice content, only metadata

    Args:
        logger: Logger instance
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        **metadata: Additional structured metadata fields

    Example:
        log_with_metadata(
            logger,
            "INFO",
            "Invoice parsed successfully",
            file_name="invoice.pdf",
            processing_time_ms=8500,
            confidence_score=0.94
        )
    """
    log_func = getattr(logger, level.lower())
    log_func(message, extra=metadata)
