"""Exceptions for Discogs API client.

Defines specific exception types for different API error conditions,
making error handling more precise and testable.
"""


class DiscogsAPIError(Exception):
    """Base exception for all Discogs API errors.

    All API-related exceptions inherit from this base class,
    allowing catching of any API error with a single except clause.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize API error.Bron

        Args:
            message: Error message describing what went wrong
            status_code: HTTP status code if available
        """
        self.status_code = status_code
        super().__init__(message)

    def __str__(self) -> str:
        """Format error message with status code if available.

        Returns:
            Formatted error message.
        """
        if self.status_code:
            return f"[{self.status_code}] {super().__str__()}"
        return super().__str__()


class AuthenticationError(DiscogsAPIError):
    """Raised when authentication fails (HTTP 401).

    This typically means the API token is invalid, expired,
    or missing required permissions.
    """

    def __init__(self, message: str = "Invalid credentials or API token") -> None:
        """Initialize authentication error.

        Args:
            message: Error message (defaults to generic auth failure)
        """
        super().__init__(message, status_code=401)


class NotFoundError(DiscogsAPIError):
    """Raised when a requested resource is not found (HTTP 404).

    This can occur when requesting a release, user, or collection
    that doesn't exist or is private.
    """

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize not found error.

        Args:
            message: Error message (defaults to generic not found)
        """
        super().__init__(message, status_code=404)


class RateLimitExceeded(DiscogsAPIError):
    """Raised when API rate limit is exceeded (HTTP 429).

    Discogs allows 60 requests per minute for authenticated users.
    This exception is raised when that limit is exceeded.
    """

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying (from Retry-After header)
        """
        super().__init__(message, status_code=429)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Format error message with retry information.

        Returns:
            Formatted error message with retry delay if available.
        """
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} (retry after {self.retry_after}s)"
        return base_msg


class ServerError(DiscogsAPIError):
    """Raised when the server returns a 5xx error.

    These are typically temporary server issues on Discogs' side
    and may succeed if retried after a delay.
    """

    def __init__(self, message: str = "Server error", status_code: int = 500) -> None:
        """Initialize server error.

        Args:
            message: Error message
            status_code: HTTP status code (500-599)
        """
        super().__init__(message, status_code=status_code)


class NetworkError(DiscogsAPIError):
    """Raised when network connectivity issues occur.

    This wraps lower-level network exceptions like timeouts,
    connection refused, DNS failures, etc.
    """

    def __init__(self, message: str, original_exception: Exception | None = None) -> None:
        """Initialize network error.

        Args:
            message: Error message describing the network issue
            original_exception: The original exception that was caught
        """
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self) -> str:
        """Format error message with original exception if available.

        Returns:
            Formatted error message with original exception info.
        """
        base_msg = super().__str__()
        if self.original_exception:
            return f"{base_msg} (caused by: {self.original_exception!r})"
        return base_msg


class InvalidResponseError(DiscogsAPIError):
    """Raised when API response cannot be parsed or is invalid.

    This occurs when the response JSON is malformed or doesn't
    match the expected Pydantic model schema.
    """

    def __init__(self, message: str, response_text: str | None = None) -> None:
        """Initialize invalid response error.

        Args:
            message: Error message
            response_text: Raw response text that failed to parse (optional)
        """
        super().__init__(message)
        self.response_text = response_text


class PaginationError(DiscogsAPIError):
    """Raised when pagination logic encounters an error.

    This can occur when page numbers are invalid or pagination
    metadata is inconsistent.
    """

    def __init__(self, message: str) -> None:
        """Initialize pagination error.

        Args:
            message: Error message describing the pagination issue
        """
        super().__init__(message)
