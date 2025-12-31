"""Rate limiter for Discogs API requests.

Implements a token bucket algorithm to ensure API calls stay within
the Discogs rate limit of 60 requests per minute for authenticated users.
"""

import asyncio
import time
from typing import Final

from loguru import logger


class RateLimiter:
    """Token bucket rate limiter for async API calls.

    The token bucket algorithm allows bursts of requests while maintaining
    an average rate limit over time. Tokens are refilled continuously based
    on elapsed time, and each API call consumes one token.

    Attributes:
        calls: Maximum number of calls allowed per period
        period: Time period in seconds
    """

    def __init__(self, calls: int = 60, period: float = 60.0) -> None:
        """Initialize rate limiter with token bucket.

        Args:
            calls: Maximum number of calls allowed per period (default: 60)
            period: Time period in seconds (default: 60.0)
        """
        self._calls: Final[int] = calls
        self._period: Final[float] = period
        self._tokens: float = float(calls)
        self._updated_at: float = time.monotonic()
        self._lock: asyncio.Lock = asyncio.Lock()

        # Calculate refill rate (tokens per second)
        self._refill_rate: Final[float] = calls / period

        logger.debug(
            f"RateLimiter initialized: {calls} calls per {period}s "
            f"(refill rate: {self._refill_rate:.2f} tokens/s)"
        )

    async def acquire(self) -> None:
        """Acquire permission to make an API call.

        This method blocks until a token is available. It uses the token
        bucket algorithm to refill tokens based on elapsed time.

        If no tokens are available, it calculates the wait time needed
        and sleeps until a token becomes available.
        """
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._updated_at

            # Refill tokens based on elapsed time
            self._tokens = min(
                float(self._calls),
                self._tokens + elapsed * self._refill_rate,
            )
            self._updated_at = now

            # If we don't have a full token, wait until we do
            if self._tokens < 1.0:
                # Calculate wait time needed for one token
                wait_time = (1.0 - self._tokens) / self._refill_rate
                logger.debug(
                    f"Rate limit reached, waiting {wait_time:.2f}s "
                    f"(current tokens: {self._tokens:.2f})"
                )
                await asyncio.sleep(wait_time)

                # Update tokens after sleeping
                self._tokens = 1.0
                self._updated_at = time.monotonic()

            # Consume one token
            self._tokens -= 1.0
            logger.trace(f"Token acquired (remaining: {self._tokens:.2f})")  # type: ignore[attr-defined]

    async def __aenter__(self) -> "RateLimiter":
        """Async context manager entry.

        Returns:
            Self for use in async with statement.
        """
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Async context manager exit.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        pass  # No cleanup needed

    @property
    def available_tokens(self) -> float:
        """Get the current number of available tokens.

        Note: This is a snapshot and may be outdated immediately after.
        Use for debugging/monitoring only, not for decision-making.

        Returns:
            Current token count (may be fractional).
        """
        now = time.monotonic()
        elapsed = now - self._updated_at
        tokens = min(
            float(self._calls),
            self._tokens + elapsed * self._refill_rate,
        )
        return tokens

    @property
    def is_exhausted(self) -> bool:
        """Check if rate limiter is currently exhausted.

        Returns:
            True if no tokens are available (< 1.0).
        """
        return self.available_tokens < 1.0

    def reset(self) -> None:
        """Reset the rate limiter to full capacity.

        This should only be used in testing or when explicitly
        resetting the limit (e.g., after a long idle period).
        """
        self._tokens = float(self._calls)
        self._updated_at = time.monotonic()
        logger.debug("Rate limiter reset to full capacity")
