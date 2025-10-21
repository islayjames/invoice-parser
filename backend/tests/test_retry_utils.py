"""
TDD RED Phase: Retry Utility Tests
Tests for exponential backoff with OpenAI error handling per TRD Section 6.2

Expected to FAIL: Implementation doesn't exist yet
"""

import pytest
import time
import asyncio
from unittest.mock import AsyncMock, patch, Mock
from openai import RateLimitError, APITimeoutError, OpenAIError
import httpx

# This import will FAIL - implementation doesn't exist yet
from app.utils.retry import retry_with_exponential_backoff


# Helper to create proper OpenAI exceptions for testing
def create_rate_limit_error(message="Rate limit exceeded"):
    response = Mock(spec=httpx.Response)
    response.status_code = 429
    response.headers = {}
    return RateLimitError(message, response=response, body=None)


def create_timeout_error(message="Request timed out"):
    request = Mock(spec=httpx.Request)
    request.url = "https://api.openai.com/v1/test"
    request.method = "POST"
    return APITimeoutError(request=request)


class TestRetryUtility:
    """Test suite for exponential backoff retry utility"""

    @pytest.mark.asyncio
    async def test_succeeds_on_first_attempt(self):
        """Should return result immediately if function succeeds on first try"""
        mock_func = AsyncMock(return_value="success")

        start_time = time.time()
        result = await retry_with_exponential_backoff(mock_func)
        elapsed = time.time() - start_time

        assert result == "success"
        assert mock_func.call_count == 1
        assert elapsed < 0.5  # Should be near-instant

    @pytest.mark.asyncio
    async def test_retries_on_rate_limit_error(self):
        """Should retry when RateLimitError is raised"""
        mock_func = AsyncMock(
            side_effect=[
                create_rate_limit_error(),
                create_rate_limit_error(),
                "success",
            ]
        )

        result = await retry_with_exponential_backoff(mock_func)

        assert result == "success"
        assert mock_func.call_count == 3  # Failed twice, succeeded on third

    @pytest.mark.asyncio
    async def test_retries_on_timeout_error(self):
        """Should retry when APITimeoutError is raised"""
        mock_func = AsyncMock(
            side_effect=[
                create_timeout_error(),
                "success",
            ]
        )

        result = await retry_with_exponential_backoff(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_generic_openai_error(self):
        """Should retry on generic OpenAI errors"""
        mock_func = AsyncMock(
            side_effect=[
                OpenAIError("Service unavailable"),
                "success",
            ]
        )

        result = await retry_with_exponential_backoff(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_fails_after_max_retries(self):
        """Should raise exception after max_retries (3) attempts"""
        error = create_rate_limit_error()
        mock_func = AsyncMock(side_effect=error)

        with pytest.raises(RateLimitError):
            await retry_with_exponential_backoff(mock_func, max_retries=3)

        # Should attempt: initial + 3 retries = 4 total calls
        assert mock_func.call_count == 4

    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self):
        """Should use exponential backoff: 1s, 2s, 4s pattern"""
        mock_func = AsyncMock(
            side_effect=[
                create_rate_limit_error(),
                create_rate_limit_error(),
                create_rate_limit_error(),
                "success",
            ]
        )

        delays = []

        with patch("asyncio.sleep") as mock_sleep:
            mock_sleep.side_effect = lambda delay: delays.append(delay)

            result = await retry_with_exponential_backoff(
                mock_func,
                max_retries=3,
                initial_delay=1.0,
                backoff_factor=2.0,
                jitter=False,  # Disable jitter for predictable testing
            )

            assert result == "success"
            assert len(delays) == 3

            # Verify exponential pattern: 1s, 2s, 4s
            assert delays[0] == pytest.approx(1.0, abs=0.01)
            assert delays[1] == pytest.approx(2.0, abs=0.01)
            assert delays[2] == pytest.approx(4.0, abs=0.01)

    @pytest.mark.asyncio
    async def test_jitter_adds_randomness(self):
        """Should add random jitter to delays to prevent thundering herd"""
        mock_func = AsyncMock(
            side_effect=[
                create_rate_limit_error(),
                create_rate_limit_error(),
                "success",
            ]
        )

        delays = []

        with patch("asyncio.sleep") as mock_sleep:
            mock_sleep.side_effect = lambda delay: delays.append(delay)

            result = await retry_with_exponential_backoff(
                mock_func,
                max_retries=2,
                initial_delay=1.0,
                backoff_factor=2.0,
                jitter=True,  # Enable jitter
            )

            assert result == "success"
            assert len(delays) == 2

            # With jitter, delays should vary from base (0.5x to 1.5x)
            # First delay: 1.0s ± jitter (0.5 to 1.5)
            # Second delay: 2.0s ± jitter (1.0 to 3.0)
            assert 0.5 <= delays[0] <= 1.5
            assert 1.0 <= delays[1] <= 3.0

            # Delays should not be exactly the base values
            # (statistically very unlikely with jitter)
            assert delays[0] != 1.0 or delays[1] != 2.0

    @pytest.mark.asyncio
    async def test_propagates_non_retryable_errors(self):
        """Should immediately raise errors that are not retryable"""
        mock_func = AsyncMock(side_effect=ValueError("Invalid argument"))

        with pytest.raises(ValueError, match="Invalid argument"):
            await retry_with_exponential_backoff(mock_func)

        # Should not retry on non-OpenAI errors
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_custom_max_retries(self):
        """Should respect custom max_retries parameter"""
        error = create_rate_limit_error()
        mock_func = AsyncMock(side_effect=error)

        with pytest.raises(RateLimitError):
            await retry_with_exponential_backoff(mock_func, max_retries=1)

        # Initial attempt + 1 retry = 2 calls
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_custom_initial_delay(self):
        """Should use custom initial_delay parameter"""
        mock_func = AsyncMock(
            side_effect=[
                create_rate_limit_error(),
                "success",
            ]
        )

        delays = []

        with patch("asyncio.sleep") as mock_sleep:
            mock_sleep.side_effect = lambda delay: delays.append(delay)

            result = await retry_with_exponential_backoff(
                mock_func,
                initial_delay=0.5,  # Custom 0.5s initial delay
                jitter=False,
            )

            assert result == "success"
            assert delays[0] == pytest.approx(0.5, abs=0.01)

    @pytest.mark.asyncio
    async def test_custom_backoff_factor(self):
        """Should use custom backoff_factor parameter"""
        mock_func = AsyncMock(
            side_effect=[
                create_rate_limit_error(),
                create_rate_limit_error(),
                "success",
            ]
        )

        delays = []

        with patch("asyncio.sleep") as mock_sleep:
            mock_sleep.side_effect = lambda delay: delays.append(delay)

            result = await retry_with_exponential_backoff(
                mock_func,
                initial_delay=1.0,
                backoff_factor=3.0,  # Custom 3x backoff
                jitter=False,
            )

            assert result == "success"
            # Should be: 1.0s, 3.0s (1.0 * 3)
            assert delays[0] == pytest.approx(1.0, abs=0.01)
            assert delays[1] == pytest.approx(3.0, abs=0.01)

    @pytest.mark.asyncio
    async def test_preserves_function_arguments(self):
        """Should pass arguments to wrapped function correctly"""
        mock_func = AsyncMock(return_value="success")

        result = await retry_with_exponential_backoff(
            mock_func,
            "arg1",
            "arg2",
            kwarg1="value1",
            kwarg2="value2",
        )

        assert result == "success"
        mock_func.assert_called_once_with(
            "arg1",
            "arg2",
            kwarg1="value1",
            kwarg2="value2",
        )

    @pytest.mark.asyncio
    async def test_logs_retry_attempts(self):
        """Should log retry attempts for debugging"""
        mock_func = AsyncMock(
            side_effect=[
                create_rate_limit_error(),
                "success",
            ]
        )

        with patch("app.utils.retry.logger") as mock_logger:
            result = await retry_with_exponential_backoff(mock_func)

            assert result == "success"

            # Should log the retry attempt
            assert mock_logger.warning.called or mock_logger.info.called

    @pytest.mark.asyncio
    async def test_async_function_compatibility(self):
        """Should work with async functions"""
        # Test with failure then success
        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise create_rate_limit_error()
            return "success"

        result = await retry_with_exponential_backoff(failing_then_success)
        assert result == "success"
        assert call_count == 2
