"""Rate limiter implementation using sliding window algorithm."""

import time
from collections import deque


class RateLimiter:
    """Rate limiter using sliding window algorithm."""

    def __init__(self, requests_per_minute: int) -> None:
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum number of requests allowed per minute.
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = 60.0  # 60 seconds
        self.requests: deque[float] = deque()

    def acquire(self) -> None:
        """Acquire permission to make a request.

        Blocks if rate limit is exceeded until a slot becomes available.
        """
        now = time.time()
        # Remove requests outside the current window
        while self.requests and now - self.requests[0] > self.window_size:
            self.requests.popleft()

        if len(self.requests) >= self.requests_per_minute:
            # Calculate sleep time until oldest request expires
            sleep_time = self.window_size - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            # Clean up after sleep
            now = time.time()
            while self.requests and now - self.requests[0] > self.window_size:
                self.requests.popleft()

        self.requests.append(now)

    def get_current_usage(self) -> dict[str, int]:
        """Get current usage statistics.

        Returns:
            Dictionary with 'current_requests' and 'max_requests'.
        """
        now = time.time()
        # Clean up old requests
        while self.requests and now - self.requests[0] > self.window_size:
            self.requests.popleft()

        return {
            "current_requests": len(self.requests),
            "max_requests": self.requests_per_minute,
        }

    def get_remaining_capacity(self) -> tuple[int, int]:
        """Get remaining capacity.

        Returns:
            Tuple of (remaining_requests, max_requests).
        """
        usage = self.get_current_usage()
        remaining = usage["max_requests"] - usage["current_requests"]
        return remaining, usage["max_requests"]
