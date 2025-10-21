"""
Retry Utility with Exponential Backoff

Provides resilient error handling for transient OpenAI API failures.
Implements exponential backoff with jitter per TRD Section 6.2 to handle:
- Rate limit errors (429)
- Timeout errors
- Transient API failures

Usage Example:
    ```python
    from openai import AsyncOpenAI
    from app.utils.retry import retry_with_exponential_backoff

    client = AsyncOpenAI(api_key="...")

    async def call_gpt4o(prompt: str) -> str:
        # Wrap OpenAI API call with retry logic
        response = await retry_with_exponential_backoff(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_retries=3,
            initial_delay=1.0
        )
        return response.choices[0].message.content
    ```

Retry Strategy:
    - Initial delay: 1 second
    - Backoff factor: 2x (exponential)
    - Jitter: ±50% randomization to prevent thundering herd
    - Max retries: 3 attempts (configurable)

Calculation Example (jitter disabled):
    - Attempt 1 fails → wait 1.0s (initial_delay * 2^0)
    - Attempt 2 fails → wait 2.0s (initial_delay * 2^1)
    - Attempt 3 fails → wait 4.0s (initial_delay * 2^2)
    - Attempt 4 (final) fails → raise exception

With jitter enabled (default):
    - Delays randomized by ±50% to prevent synchronized retries
    - Example: 2.0s → random value between 1.0s and 3.0s

Performance Impact:
    - Worst case (3 retries): ~7 seconds added delay (1s + 2s + 4s)
    - With jitter: ~3.5s to ~10.5s added delay
    - Trade-off: Resilience vs. latency for transient errors
"""

import asyncio
import random
import logging
from typing import Callable, Any, TypeVar
from openai import RateLimitError, APITimeoutError, OpenAIError

logger = logging.getLogger(__name__)

# Type variable for generic return type
T = TypeVar('T')


async def retry_with_exponential_backoff(
    func: Callable[..., T],
    *args: Any,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    **kwargs: Any
) -> T:
    """
    Retry async function with exponential backoff on transient OpenAI API errors.

    Implements resilient retry logic for OpenAI API calls that may fail due to:
    - Rate limiting (HTTP 429)
    - Timeouts (network or API processing)
    - Transient service errors (5xx errors)

    The function uses exponential backoff with optional jitter to:
    1. Prevent overwhelming the API during high load
    2. Avoid "thundering herd" problem (synchronized retries)
    3. Maximize chances of success for transient failures

    Args:
        func: Async callable to retry (e.g., OpenAI API method).
              Must be an async function that can be awaited.
        *args: Positional arguments forwarded to func.
        max_retries: Maximum number of retry attempts after initial failure.
                     Total attempts = max_retries + 1 (initial attempt).
                     Default: 3 (total 4 attempts).
        initial_delay: Starting delay in seconds before first retry.
                      Each subsequent delay is multiplied by backoff_factor.
                      Default: 1.0 second.
        backoff_factor: Exponential multiplier for delay calculation.
                       delay = initial_delay * (backoff_factor ** attempt)
                       Default: 2.0 (doubles each retry: 1s, 2s, 4s, 8s...).
        jitter: Whether to add randomization to delays (±50%).
               Prevents synchronized retries from multiple clients.
               Default: True (recommended for production).
        **kwargs: Keyword arguments forwarded to func.

    Returns:
        T: Return value from successful func() invocation.
           Type matches the return type of func.

    Raises:
        RateLimitError: After max_retries exhausted for rate limit errors
        APITimeoutError: After max_retries exhausted for timeout errors
        OpenAIError: After max_retries exhausted for other OpenAI errors
        Exception: Non-retryable errors are propagated immediately without retry

    Example:
        ```python
        from openai import AsyncOpenAI
        from app.utils.retry import retry_with_exponential_backoff

        client = AsyncOpenAI()

        # Retry OpenAI API call with custom parameters
        result = await retry_with_exponential_backoff(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[{"role": "user", "content": "Parse this invoice..."}],
            max_retries=5,          # Up to 6 total attempts
            initial_delay=2.0,      # Start with 2s delay
            backoff_factor=3.0,     # Triple delay each retry (2s, 6s, 18s...)
            jitter=True             # Randomize delays
        )
        ```

    Performance Notes:
        - Each retry adds exponential delay to total request time
        - With defaults (3 retries), worst case adds ~7s (1s+2s+4s)
        - Trade-off: Resilience vs. latency (acceptable for NFR-001: <20s parse time)
        - Non-retryable errors fail immediately without delay

    Implementation Details:
        - Only retries transient OpenAI errors (rate limit, timeout, API errors)
        - All other exceptions (validation, programming errors) fail fast
        - Logs all retry attempts with delay duration for debugging
        - Final failure logs error and re-raises for caller handling
    """
    # Define which OpenAI exceptions are transient and worth retrying
    # These typically indicate temporary issues, not permanent failures
    retryable_errors = (
        RateLimitError,    # HTTP 429 - too many requests, retry after backoff
        APITimeoutError,   # Request/response timeout, network or API latency
        OpenAIError,       # Generic OpenAI error, may be transient (5xx errors)
    )

    # Retry loop: attempt 0 = initial call, attempts 1-N = retries
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            # Execute the async function with provided arguments
            # If successful, return immediately (no retries needed)
            result = await func(*args, **kwargs)

            # Log success if this was a retry (not initial attempt)
            if attempt > 0:
                logger.info(
                    f"Function '{func.__name__}' succeeded on retry attempt {attempt}/{max_retries}"
                )

            return result

        except retryable_errors as e:
            # Check if we've exhausted all retry attempts
            if attempt >= max_retries:
                logger.error(
                    f"Max retries ({max_retries}) exhausted for '{func.__name__}'. "
                    f"Final error: {type(e).__name__}: {str(e)}"
                )
                raise  # Re-raise the exception for caller to handle

            # Calculate exponential backoff delay
            # Formula: delay = initial_delay * (backoff_factor ^ attempt)
            # Example: 1.0 * (2.0 ^ 0) = 1.0s, 1.0 * (2.0 ^ 1) = 2.0s, etc.
            delay = initial_delay * (backoff_factor ** attempt)

            # Add jitter (random variance) to prevent thundering herd
            # Randomizes delay by ±50% (multiply by 0.5 to 1.5)
            # Example: 2.0s becomes random value between 1.0s and 3.0s
            if jitter:
                jitter_factor = random.uniform(0.5, 1.5)
                delay = delay * jitter_factor

            # Log retry attempt with detailed context for debugging
            logger.warning(
                f"Retry attempt {attempt + 1}/{max_retries} for '{func.__name__}' "
                f"after {delay:.2f}s delay. Error encountered: {type(e).__name__}: {str(e)}"
            )

            # Sleep for calculated delay before next retry
            await asyncio.sleep(delay)

        except Exception as e:
            # Non-retryable error detected (not in retryable_errors tuple)
            # These are likely programming errors or validation failures
            # Fail fast without retry to avoid wasting time
            logger.error(
                f"Non-retryable error in '{func.__name__}': {type(e).__name__}: {str(e)}. "
                f"Failing immediately without retry."
            )
            raise  # Propagate immediately to caller
