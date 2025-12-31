"""Collection fetching and management.

Handles fetching the user's collection from the Discogs API with
progress tracking, resume capability, and error handling.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

from loguru import logger

from discogs_dumper.api.client import DiscogsClient
from discogs_dumper.api.exceptions import DiscogsAPIError
from discogs_dumper.api.models import Release
from discogs_dumper.persistence.models import ProgressState
from discogs_dumper.persistence.state import StateManager


class CollectionFetcher:
    """Fetches and manages collection data from Discogs API.

    Provides progress tracking, resume capability, and automatic state
    persistence during collection fetching.

    Attributes:
        client: Async Discogs API client
        username: Discogs username
        state: Current progress state
        save_interval_items: Save state every N items
        save_interval_seconds: Save state every N seconds

    Examples:
        >>> async with DiscogsClient(username, token) as client:
        ...     fetcher = CollectionFetcher(client, username)
        ...     releases = await fetcher.fetch_all()
        ...     print(f"Fetched {len(releases)} releases")
    """

    def __init__(
        self,
        client: DiscogsClient,
        username: str,
        *,
        save_interval_items: int = 50,
        save_interval_seconds: float = 30.0,
        resume: bool = False,
    ) -> None:
        """Initialize collection fetcher.

        Args:
            client: Initialized Discogs API client
            username: Discogs username
            save_interval_items: Save state every N items (default: 50)
            save_interval_seconds: Save state every N seconds (default: 30.0)
            resume: Resume from previous state if available (default: False)
        """
        self.client = client
        self.username = username
        self.save_interval_items = save_interval_items
        self.save_interval_seconds = save_interval_seconds

        # Initialize or load state
        if resume and StateManager.has_state():
            loaded_state = StateManager.load_state(username=username)
            if loaded_state:
                self.state = loaded_state
                logger.info(
                    f"Resuming from previous state: "
                    f"{self.state.fetched_items}/{self.state.total_items} items"
                )
            else:
                self.state = self._create_initial_state()
        else:
            self.state = self._create_initial_state()

        self._last_save_time = datetime.now(timezone.utc)

    def _create_initial_state(self) -> ProgressState:
        """Create initial progress state.

        Returns:
            New ProgressState with current timestamp
        """
        now = datetime.now(timezone.utc)
        return ProgressState(
            username=self.username,
            started_at=now,
            last_updated=now,
            total_items=0,
            fetched_items=0,
        )

    def _should_save_state(self) -> bool:
        """Check if state should be saved based on intervals.

        Returns:
            True if state should be saved, False otherwise
        """
        # Save based on item count
        if self.state.fetched_items % self.save_interval_items == 0:
            return True

        # Save based on time elapsed
        elapsed = (datetime.now(timezone.utc) - self._last_save_time).total_seconds()
        if elapsed >= self.save_interval_seconds:
            return True

        return False

    def _save_state(self) -> None:
        """Save current progress state."""
        self.state.last_updated = datetime.now(timezone.utc)
        StateManager.save_state(self.state)
        self._last_save_time = datetime.now(timezone.utc)
        logger.debug(
            f"State saved: {self.state.fetched_items}/{self.state.total_items} items"
        )

    async def fetch_all(
        self,
        *,
        per_page: int = 100,
        max_concurrent: int = 5,
        progress_callback: Any = None,
    ) -> list[Release]:
        """Fetch all releases from user's collection.

        Fetches all releases with automatic pagination, progress tracking,
        and periodic state persistence.

        Args:
            per_page: Items per API page (default: 100, max: 100)
            max_concurrent: Max concurrent page fetches (default: 5)
            progress_callback: Optional callback function called with
                (current, total) after each item

        Returns:
            List of all releases in collection

        Raises:
            DiscogsAPIError: If API request fails

        Examples:
            >>> async def progress(current, total):
            ...     print(f"Progress: {current}/{total}")
            >>> releases = await fetcher.fetch_all(progress_callback=progress)
        """
        logger.info(f"Fetching collection for user '{self.username}'")

        try:
            # Get first page to determine total items from pagination
            first_page = await self.client.get_collection_page(page=1, per_page=per_page)
            total_items = first_page.pagination.items

            # Update state with total
            self.state = StateManager.get_or_create_state(
                username=self.username,
                total_items=total_items,
            )

            logger.info(f"Collection contains {total_items} items")

            releases: list[Release] = []

            # Fetch all releases using async iterator
            async for release in self.client.get_collection_all(
                per_page=per_page,
                max_concurrent=max_concurrent,
            ):
                releases.append(release)
                self.state.fetched_items = len(releases)

                # Progress callback
                if progress_callback:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(len(releases), total_items)
                    else:
                        progress_callback(len(releases), total_items)

                # Periodic state saving
                if self._should_save_state():
                    self._save_state()

            # Final state save
            self._save_state()

            logger.info(f"Successfully fetched {len(releases)} releases")
            return releases

        except DiscogsAPIError as e:
            logger.error(f"Failed to fetch collection: {e}")
            # Save state before re-raising
            self._save_state()
            raise

    async def fetch_incremental(
        self,
        *,
        per_page: int = 100,
        progress_callback: Any = None,
    ) -> list[Release]:
        """Fetch only new/unfetched releases from collection.

        Uses saved state to fetch only releases that haven't been
        fetched yet. Useful for resuming interrupted operations.

        Args:
            per_page: Items per API page (default: 100)
            progress_callback: Optional callback function

        Returns:
            List of newly fetched releases

        Raises:
            DiscogsAPIError: If API request fails

        Examples:
            >>> # Fetch first 50 items
            >>> releases = await fetcher.fetch_all()
            >>> # Later, resume and fetch remaining
            >>> fetcher2 = CollectionFetcher(client, username, resume=True)
            >>> new_releases = await fetcher2.fetch_incremental()
        """
        logger.info(
            f"Fetching incremental updates: "
            f"{self.state.fetched_items}/{self.state.total_items} already fetched"
        )

        if self.state.fetched_items >= self.state.total_items:
            logger.info("Collection already fully fetched")
            return []

        try:
            all_releases: list[Release] = []
            fetched_count = 0

            async for release in self.client.get_collection_all(per_page=per_page):
                # Skip already-fetched items
                if fetched_count < self.state.fetched_items:
                    fetched_count += 1
                    continue

                all_releases.append(release)
                self.state.fetched_items = self.state.fetched_items + 1

                # Progress callback
                if progress_callback:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(
                            self.state.fetched_items,
                            self.state.total_items,
                        )
                    else:
                        progress_callback(
                            self.state.fetched_items,
                            self.state.total_items,
                        )

                # Periodic state saving
                if self._should_save_state():
                    self._save_state()

            # Final state save
            self._save_state()

            logger.info(f"Fetched {len(all_releases)} new releases")
            return all_releases

        except DiscogsAPIError as e:
            logger.error(f"Failed to fetch incremental updates: {e}")
            self._save_state()
            raise

    def clear_state(self) -> None:
        """Clear saved progress state.

        Removes the saved state file for this username.
        """
        StateManager.clear_state(username=self.username)
        logger.info(f"Cleared progress state for '{self.username}'")


async def fetch_collection(
    username: str,
    token: str,
    *,
    resume: bool = False,
    progress_callback: Any = None,
) -> list[Release]:
    """Convenience function to fetch entire collection.

    Creates a client, fetches all releases, and cleans up automatically.

    Args:
        username: Discogs username
        token: Discogs API token
        resume: Resume from saved state (default: False)
        progress_callback: Optional progress callback function

    Returns:
        List of all releases in collection

    Raises:
        DiscogsAPIError: If API request fails

    Examples:
        >>> releases = await fetch_collection("buntstift", "my-token")
        >>> print(f"Found {len(releases)} releases")
    """
    async with DiscogsClient(username=username, token=token) as client:
        fetcher = CollectionFetcher(client, username, resume=resume)
        return await fetcher.fetch_all(progress_callback=progress_callback)
