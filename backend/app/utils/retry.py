"""
Retry Utility with Exponential Backoff
Handles transient OpenAI API errors with exponential backoff per TRD Section 6.2
"""

import asyncio
import random
import logging
from typing import Callable, Any
from openai import RateLimitError, APITimeoutError, OpenAIError

logger = logging.getLogger(__name__)


async def retry_with_exponential_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    **kwargs
) -> Any:
    """
    Retry async function with exponential backoff on OpenAI errors.

    Args:
        func: Async function to retry
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        jitter: Add random jitter to delays (default: True)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of successful function call

    Raises:
        Exception: Re-raises last exception after max_retries exhausted
        Non-retryable exceptions are propagated immediately
    """
    retryable_errors = (RateLimitError, APITimeoutError, OpenAIError)

    for attempt in range(max_retries + 1):  # Initial attempt + retries
        try:
            # Call the async function
            result = await func(*args, **kwargs)
            return result

        except retryable_errors as e:
            # If this was the last attempt, raise the exception
            if attempt >= max_retries:
                logger.error(
                    f"Max retries ({max_retries}) exhausted for {func.__name__}: {e}"
                )
                raise

            # Calculate delay with exponential backoff
            delay = initial_delay * (backoff_factor ** attempt)

            # Add jitter to prevent thundering herd (±50%)
            if jitter:
                delay = delay * random.uniform(0.5, 1.5)

            # Log retry attempt
            logger.warning(
                f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                f"after {delay:.2f}s delay. Error: {e}"
            )

            # Wait before retrying
            await asyncio.sleep(delay)

        except Exception as e:
            # Non-retryable error - propagate immediately
            logger.error(f"Non-retryable error in {func.__name__}: {e}")
            raise
