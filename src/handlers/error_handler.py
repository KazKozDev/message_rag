"""Error handling with retry logic."""

import functools
import time
from collections.abc import Callable
from typing import Any


class APIError(Exception):
    """Base exception for API errors."""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded exception."""

    pass


class TimeoutError(APIError):
    """Request timeout exception."""

    pass


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier for exponential delay.
        exceptions: Tuple of exception types to catch and retry.

    Returns:
        Decorated function with retry logic.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # Max retries exhausted
                        raise last_exception from e

            # This should never be reached, but for type safety
            if last_exception:
                raise last_exception

        return wrapper

    return decorator
