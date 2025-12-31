"""Async Discogs API client.

Provides an asynchronous client for interacting with the Discogs API v2,
with built-in rate limiting, error handling, and Pydantic model validation.
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import aiohttp
from loguru import logger
from pydantic import ValidationError

from discogs_dumper.api.exceptions import (
    AuthenticationError,
    DiscogsAPIError,
    InvalidResponseError,
    NetworkError,
    NotFoundError,
    RateLimitExceeded,
    ServerError,
)
from discogs_dumper.api.models import CollectionPage, CollectionValue, Release
from discogs_dumper.api.rate_limiter import RateLimiter


class DiscogsClient:
    """Async client for Discogs API v2.

    Handles authentication, rate limiting, and response parsing.
    Use as an async context manager to ensure proper cleanup.

    Example:
        async with DiscogsClient("username", "token") as client:
            value = await client.get_collection_value()
            releases = [r async for r in client.get_collection_all()]
    """

    def __init__(
        self,
        username: str,
        token: str,
        base_url: str = "https://api.discogs.com",
        user_agent: str = "DiscogsCollectionDumper/2.0.0",
        rate_limit_calls: int = 60,
        rate_limit_period: float = 60.0,
    ) -> None:
        """Initialize Discogs API client.

        Args:
            username: Discogs username
            token: Discogs API token (from developer settings)
            base_url: API base URL (default: https://api.discogs.com)
            user_agent: User-Agent header (required by Discogs)
            rate_limit_calls: Max API calls per period (default: 60)
            rate_limit_period: Rate limit period in seconds (default: 60.0)
        """
        self.username = username
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._user_agent = user_agent

        # Rate limiter for API calls
        self._rate_limiter = RateLimiter(calls=rate_limit_calls, period=rate_limit_period)

        # aiohttp session (created in __aenter__)
        self._session: aiohttp.ClientSession | None = None

        # Default headers for all requests
        self._headers = {
            "User-Agent": user_agent,
            "Accept": "application/vnd.discogs.v2.plaintext+json",
            "Content-Type": "application/json",
            "Authorization": f"Discogs token={token}",
        }

        logger.info(f"DiscogsClient initialized for user: {username}")

    async def __aenter__(self) -> "DiscogsClient":
        """Async context manager entry - create aiohttp session.

        Returns:
            Self for use in async with statement.
        """
        self._session = aiohttp.ClientSession(headers=self._headers)
        logger.debug("aiohttp session created")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Async context manager exit - close aiohttp session.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if self._session:
            await self._session.close()
            logger.debug("aiohttp session closed")

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Discogs API.

        Handles rate limiting, error responses, and JSON parsing.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/users/{username}/collection/value")
            params: Query parameters (optional)

        Returns:
            Parsed JSON response as dictionary.

        Raises:
            AuthenticationError: If credentials are invalid (401)
            NotFoundError: If resource not found (404)
            RateLimitExceeded: If rate limit exceeded (429)
            ServerError: If server error occurs (5xx)
            NetworkError: If network/connection error occurs
            InvalidResponseError: If response cannot be parsed
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with DiscogsClient(...)'")

        # Acquire rate limit token
        await self._rate_limiter.acquire()

        url = f"{self._base_url}{endpoint}"
        logger.debug(f"{method} {url} (params: {params})")

        try:
            async with self._session.request(
                method,
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                # Handle different HTTP status codes
                if response.status == 401:
                    raise AuthenticationError("Invalid API token or insufficient permissions")

                if response.status == 404:
                    text = await response.text()
                    raise NotFoundError(f"Resource not found: {url} ({text})")

                if response.status == 429:
                    # Try to get retry-after header
                    retry_after = response.headers.get("Retry-After")
                    retry_seconds = int(retry_after) if retry_after else None
                    raise RateLimitExceeded(
                        "API rate limit exceeded",
                        retry_after=retry_seconds,
                    )

                if response.status >= 500:
                    text = await response.text()
                    raise ServerError(
                        f"Server error: {response.status}",
                        status_code=response.status,
                    )

                if response.status != 200:
                    text = await response.text()
                    raise DiscogsAPIError(
                        f"Unexpected status {response.status}: {text}",
                        status_code=response.status,
                    )

                # Parse JSON response
                try:
                    data: dict[str, Any] = await response.json()
                    logger.trace(f"Response: {len(str(data))} bytes")  # type: ignore[attr-defined]
                    return data
                except aiohttp.ContentTypeError as e:
                    text = await response.text()
                    raise InvalidResponseError(
                        f"Invalid JSON response: {e}",
                        response_text=text,
                    ) from e

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}", original_exception=e) from e
        except asyncio.TimeoutError as e:
            raise NetworkError("Request timeout", original_exception=e) from e

    async def get_collection_value(self) -> CollectionValue:
        """Get collection value statistics (min/median/max).

        Returns:
            CollectionValue with minimum, median, and maximum values.

        Raises:
            AuthenticationError: If credentials invalid
            DiscogsAPIError: On other API errors
            ValidationError: If response doesn't match expected schema
        """
        endpoint = f"/users/{self.username}/collection/value"
        data = await self._request("GET", endpoint)

        try:
            return CollectionValue.model_validate(data)
        except ValidationError as e:
            logger.error(f"Validation error for collection value: {e}")
            raise InvalidResponseError(
                f"Invalid collection value response: {e}",
                response_text=str(data),
            ) from e

    async def get_collection_page(
        self,
        page: int = 1,
        per_page: int = 100,
    ) -> CollectionPage:
        """Get a single page of collection releases.

        Args:
            page: Page number (1-indexed)
            per_page: Number of releases per page (max 100)

        Returns:
            CollectionPage with pagination info and releases.

        Raises:
            AuthenticationError: If credentials invalid
            DiscogsAPIError: On other API errors
            ValidationError: If response doesn't match expected schema
        """
        endpoint = f"/users/{self.username}/collection/folders/0/releases"
        params = {
            "page": str(page),
            "per_page": str(min(per_page, 100)),  # Discogs max is 100
        }

        data = await self._request("GET", endpoint, params=params)

        try:
            return CollectionPage.model_validate(data)
        except ValidationError as e:
            logger.error(f"Validation error for collection page: {e}")
            raise InvalidResponseError(
                f"Invalid collection page response: {e}",
                response_text=str(data),
            ) from e

    async def get_collection_all(
        self,
        per_page: int = 100,
        max_concurrent: int = 5,
    ) -> AsyncIterator[Release]:
        """Get all releases from collection with concurrent pagination.

        This method first fetches the first page to determine total pages,
        then concurrently fetches remaining pages for better performance.

        Args:
            per_page: Number of releases per page (max 100)
            max_concurrent: Maximum number of concurrent page fetches

        Yields:
            Individual Release objects from the collection.

        Raises:
            AuthenticationError: If credentials invalid
            DiscogsAPIError: On other API errors
        """
        # Fetch first page to get total pages
        first_page = await self.get_collection_page(page=1, per_page=per_page)

        logger.info(
            f"Collection: {first_page.pagination.items} items, "
            f"{first_page.pagination.pages} pages"
        )

        # Yield releases from first page
        for release in first_page.releases:
            yield release

        # If only one page, we're done
        if first_page.pagination.pages == 1:
            return

        # Fetch remaining pages concurrently
        total_pages = first_page.pagination.pages

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_page(page_num: int) -> CollectionPage:
            """Fetch a single page with semaphore."""
            async with semaphore:
                return await self.get_collection_page(page=page_num, per_page=per_page)

        # Create tasks for all remaining pages
        tasks = [fetch_page(page) for page in range(2, total_pages + 1)]

        # Process pages as they complete
        for coro in asyncio.as_completed(tasks):
            page_data = await coro
            for release in page_data.releases:
                yield release

    async def test_connection(self) -> bool:
        """Test API connection and credentials.

        Returns:
            True if connection successful and credentials valid.

        Raises:
            DiscogsAPIError: On connection or authentication failure.
        """
        try:
            await self.get_collection_value()
            logger.info("API connection test successful")
            return True
        except AuthenticationError:
            logger.error("API connection test failed: Invalid credentials")
            raise
        except DiscogsAPIError as e:
            logger.error(f"API connection test failed: {e}")
            raise
