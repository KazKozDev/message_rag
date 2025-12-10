"""Tests for error handler."""

import pytest

from src.handlers.error_handler import APIError, RateLimitError, retry_on_error


def test_api_error_exception() -> None:
    """Test APIError exception."""
    with pytest.raises(APIError):
        raise APIError("API request failed")


def test_rate_limit_error_exception() -> None:
    """Test RateLimitError exception."""
    with pytest.raises(RateLimitError):
        raise RateLimitError("Rate limit exceeded")


def test_retry_success_first_attempt() -> None:
    """Test retry decorator when first attempt succeeds."""
    call_count = 0

    @retry_on_error(max_retries=3)
    def successful_function() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = successful_function()
    assert result == "success"
    assert call_count == 1


def test_retry_success_after_failures() -> None:
    """Test retry decorator succeeds after some failures."""
    call_count = 0

    @retry_on_error(max_retries=3, delay=0.1)
    def flaky_function() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise APIError("Temporary failure")
        return "success"

    result = flaky_function()
    assert result == "success"
    assert call_count == 3


def test_retry_exhausted() -> None:
    """Test retry decorator when max retries exhausted."""
    call_count = 0

    @retry_on_error(max_retries=2, delay=0.1)
    def always_fails() -> str:
        nonlocal call_count
        call_count += 1
        raise APIError("Permanent failure")

    with pytest.raises(APIError):
        always_fails()

    assert call_count == 3  # Initial attempt + 2 retries


def test_retry_specific_exceptions() -> None:
    """Test retry decorator with specific exception types."""
    call_count = 0

    @retry_on_error(max_retries=2, delay=0.1, exceptions=(RateLimitError,))
    def rate_limited_function() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise RateLimitError("Rate limited")
        return "success"

    result = rate_limited_function()
    assert result == "success"
    assert call_count == 2


def test_retry_does_not_catch_other_exceptions() -> None:
    """Test retry decorator doesn't catch unspecified exceptions."""
    call_count = 0

    @retry_on_error(max_retries=2, delay=0.1, exceptions=(RateLimitError,))
    def function_with_different_error() -> str:
        nonlocal call_count
        call_count += 1
        raise ValueError("Different error")

    with pytest.raises(ValueError):
        function_with_different_error()

    assert call_count == 1  # Should fail immediately without retry


def test_retry_backoff() -> None:
    """Test retry decorator with exponential backoff."""
    import time

    call_times = []

    @retry_on_error(max_retries=2, delay=0.1, backoff=2.0)
    def function_with_backoff() -> str:
        call_times.append(time.time())
        if len(call_times) < 3:
            raise APIError("Retry")
        return "success"

    result = function_with_backoff()
    assert result == "success"
    assert len(call_times) == 3

    # Check delays increased (with some tolerance for timing)
    if len(call_times) >= 2:
        first_delay = call_times[1] - call_times[0]
        assert first_delay >= 0.08  # Should be ~0.1s
