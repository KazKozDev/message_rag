"""Tests for rate limiter."""

import time

from src.utils.rate_limiter import RateLimiter


def test_rate_limiter_initialization() -> None:
    """Test rate limiter initialization."""
    limiter = RateLimiter(requests_per_minute=10)
    assert limiter.requests_per_minute == 10
    assert limiter.window_size == 60.0
    assert len(limiter.requests) == 0


def test_rate_limiter_allows_requests_under_limit() -> None:
    """Test that requests under limit are allowed immediately."""
    limiter = RateLimiter(requests_per_minute=5)

    start = time.time()
    for _ in range(3):
        limiter.acquire()
    elapsed = time.time() - start

    # Should be nearly instant (less than 0.1 seconds)
    assert elapsed < 0.1


def test_rate_limiter_blocks_when_exceeded() -> None:
    """Test that rate limiter blocks when limit is exceeded."""
    limiter = RateLimiter(requests_per_minute=2)

    # First 2 requests should be immediate
    limiter.acquire()
    limiter.acquire()

    # Third request should block until window resets
    start = time.time()
    limiter.acquire()
    elapsed = time.time() - start

    # Should have waited close to window size (with some tolerance)
    assert elapsed >= 0.5  # At least some delay


def test_rate_limiter_usage_stats() -> None:
    """Test usage statistics."""
    limiter = RateLimiter(requests_per_minute=10)

    # Initially empty
    usage = limiter.get_current_usage()
    assert usage["current_requests"] == 0
    assert usage["max_requests"] == 10

    # After some requests
    limiter.acquire()
    limiter.acquire()
    usage = limiter.get_current_usage()
    assert usage["current_requests"] == 2
    assert usage["max_requests"] == 10


def test_rate_limiter_window_reset() -> None:
    """Test that old requests are removed from window."""
    limiter = RateLimiter(requests_per_minute=5)
    limiter.window_size = 0.5  # Shorten window for testing

    limiter.acquire()
    assert limiter.get_current_usage()["current_requests"] == 1

    # Wait for window to expire
    time.sleep(0.6)

    usage = limiter.get_current_usage()
    assert usage["current_requests"] == 0


def test_rate_limiter_remaining_capacity() -> None:
    """Test remaining capacity calculation."""
    limiter = RateLimiter(requests_per_minute=10)

    remaining, max_requests = limiter.get_remaining_capacity()
    assert remaining == 10
    assert max_requests == 10

    limiter.acquire()
    limiter.acquire()

    remaining, max_requests = limiter.get_remaining_capacity()
    assert remaining == 8
    assert max_requests == 10
