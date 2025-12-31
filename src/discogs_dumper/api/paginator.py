"""Pagination utilities for Discogs API.

Provides helper functions and classes for handling paginated API responses,
making it easier to iterate through large collections.
"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from loguru import logger

from discogs_dumper.api.exceptions import PaginationError
from discogs_dumper.api.models import CollectionPage, Release

if TYPE_CHECKING:
    from discogs_dumper.api.client import DiscogsClient


async def paginate_collection(
    client: "DiscogsClient",
    per_page: int = 100,
    start_page: int = 1,
) -> AsyncIterator[Release]:
    """Paginate through entire collection sequentially.

    This is a simple sequential paginator that fetches pages one by one.
    For better performance with large collections, use DiscogsClient.get_collection_all()
    which fetches pages concurrently.

    Args:
        client: DiscogsClient instance
        per_page: Number of releases per page (max 100)
        start_page: Page to start from (default: 1, useful for resuming)

    Yields:
        Individual Release objects from the collection.

    Raises:
        PaginationError: If pagination logic fails
        DiscogsAPIError: On API errors
    """
    if start_page < 1:
        raise PaginationError(f"Invalid start_page: {start_page} (must be >= 1)")

    if per_page < 1 or per_page > 100:
        raise PaginationError(f"Invalid per_page: {per_page} (must be 1-100)")

    current_page = start_page
    total_pages: int | None = None

    while True:
        logger.debug(f"Fetching page {current_page}/{total_pages or '?'}")

        page_data: CollectionPage = await client.get_collection_page(
            page=current_page,
            per_page=per_page,
        )

        # Set total pages on first iteration
        if total_pages is None:
            total_pages = page_data.pagination.pages
            logger.info(
                f"Collection has {page_data.pagination.items} items "
                f"across {total_pages} pages"
            )

        # Validate pagination consistency
        if page_data.pagination.pages != total_pages:
            raise PaginationError(
                f"Inconsistent pagination: expected {total_pages} pages, "
                f"got {page_data.pagination.pages}"
            )

        if page_data.pagination.page != current_page:
            raise PaginationError(
                f"Page mismatch: requested page {current_page}, "
                f"got page {page_data.pagination.page}"
            )

        # Yield all releases from this page
        for release in page_data.releases:
            yield release

        # Check if we're done
        if current_page >= total_pages:
            logger.debug(f"Pagination complete: {current_page} pages fetched")
            break

        current_page += 1


class PaginationState:
    """Track state for resumable pagination.

    This class helps track pagination progress so fetching can be
    resumed if interrupted.
    """

    def __init__(
        self,
        total_items: int = 0,
        total_pages: int = 0,
        current_page: int = 1,
        fetched_items: int = 0,
    ) -> None:
        """Initialize pagination state.

        Args:
            total_items: Total number of items in collection
            total_pages: Total number of pages
            current_page: Current page being fetched
            fetched_items: Number of items fetched so far
        """
        self.total_items = total_items
        self.total_pages = total_pages
        self.current_page = current_page
        self.fetched_items = fetched_items

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage.

        Returns:
            Progress as percentage (0-100).
        """
        if self.total_items == 0:
            return 0.0
        return (self.fetched_items / self.total_items) * 100

    @property
    def remaining_items(self) -> int:
        """Calculate remaining items.

        Returns:
            Number of items not yet fetched.
        """
        return max(0, self.total_items - self.fetched_items)

    @property
    def is_complete(self) -> bool:
        """Check if pagination is complete.

        Returns:
            True if all items have been fetched.
        """
        return self.fetched_items >= self.total_items

    def update(self, page_data: CollectionPage) -> None:
        """Update state from a fetched page.

        Args:
            page_data: CollectionPage data from API
        """
        self.total_items = page_data.pagination.items
        self.total_pages = page_data.pagination.pages
        self.current_page = page_data.pagination.page
        self.fetched_items += len(page_data.releases)

    def __repr__(self) -> str:
        """String representation for debugging.

        Returns:
            Human-readable state description.
        """
        return (
            f"PaginationState(page={self.current_page}/{self.total_pages}, "
            f"items={self.fetched_items}/{self.total_items}, "
            f"progress={self.progress_percentage:.1f}%)"
        )


async def paginate_with_state(
    client: "DiscogsClient",
    state: PaginationState,
    per_page: int = 100,
) -> AsyncIterator[Release]:
    """Paginate collection with state tracking for resumability.

    This paginator updates the provided PaginationState as it fetches,
    allowing the state to be saved and used to resume later.

    Args:
        client: DiscogsClient instance
        state: PaginationState to track progress
        per_page: Number of releases per page (max 100)

    Yields:
        Individual Release objects from the collection.

    Raises:
        DiscogsAPIError: On API errors
    """
    while not state.is_complete:
        logger.debug(f"Fetching with state: {state}")

        page_data = await client.get_collection_page(
            page=state.current_page,
            per_page=per_page,
        )

        # Update state before yielding
        old_fetched = state.fetched_items
        state.update(page_data)

        # Yield all releases from this page
        for release in page_data.releases:
            yield release

        logger.debug(
            f"State updated: fetched {state.fetched_items - old_fetched} items "
            f"({state.progress_percentage:.1f}% complete)"
        )

        # Move to next page
        state.current_page += 1

        # Safety check
        if state.current_page > state.total_pages:
            break
