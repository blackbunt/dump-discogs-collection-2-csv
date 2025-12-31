"""Integration tests for collection fetching workflow.

Tests the complete flow of fetching collection data from mocked API.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from discogs_dumper.api.client import DiscogsClient
from discogs_dumper.core.collection import CollectionFetcher


@pytest.fixture
def mock_collection_page():
    """Create a mock collection page response."""
    from discogs_dumper.api.models import (
        CollectionPage,
        Pagination,
        Release,
        BasicInformation,
        Artist,
    )
    from datetime import datetime, timezone

    # Create mock releases
    releases = []
    for i in range(10):
        release = Release(
            id=1000 + i,
            instance_id=2000 + i,
            date_added=datetime.now(timezone.utc),
            rating=0,
            basic_information=BasicInformation(
                id=1000 + i,
                title=f"Test Album {i}",
                year=2020 + i,
                artists=[Artist(id=100 + i, name=f"Test Artist {i}", resource_url=f"https://api.discogs.com/artists/{100+i}")],
                labels=[],
                formats=[],
                genres=["Rock"],
                styles=["Alternative"],
                thumb="",
                cover_image="",
            ),
            notes=[],
        )
        releases.append(release)

    pagination = Pagination(
        page=1,
        pages=1,
        per_page=100,
        items=10,
        urls={},
    )

    return CollectionPage(pagination=pagination, releases=releases)


@pytest.mark.asyncio
async def test_collection_fetcher_fetch_all(mock_collection_page):
    """Test fetching all releases from collection."""
    # Create mock client
    mock_client = AsyncMock(spec=DiscogsClient)
    mock_client.get_collection_page = AsyncMock(return_value=mock_collection_page)

    # Make get_collection_all return async generator
    async def mock_get_all(*args, **kwargs):
        for release in mock_collection_page.releases:
            yield release

    mock_client.get_collection_all = mock_get_all

    # Create fetcher
    fetcher = CollectionFetcher(mock_client, "testuser")

    # Fetch all
    releases = await fetcher.fetch_all()

    # Verify
    assert len(releases) == 10
    assert releases[0].basic_information.title == "Test Album 0"
    assert releases[9].basic_information.title == "Test Album 9"
    assert fetcher.state.total_items == 10
    assert fetcher.state.fetched_items == 10


@pytest.mark.asyncio
async def test_collection_fetcher_with_progress_callback(mock_collection_page):
    """Test fetching with progress callback."""
    # Create mock client
    mock_client = AsyncMock(spec=DiscogsClient)
    mock_client.get_collection_page = AsyncMock(return_value=mock_collection_page)

    async def mock_get_all(*args, **kwargs):
        for release in mock_collection_page.releases:
            yield release

    mock_client.get_collection_all = mock_get_all

    # Create progress tracker
    progress_updates = []

    def progress_callback(current: int, total: int):
        progress_updates.append((current, total))

    # Create fetcher
    fetcher = CollectionFetcher(mock_client, "testuser")

    # Fetch all with progress
    releases = await fetcher.fetch_all(progress_callback=progress_callback)

    # Verify
    assert len(releases) == 10
    assert len(progress_updates) == 10
    assert progress_updates[0] == (1, 10)
    assert progress_updates[-1] == (10, 10)


@pytest.mark.asyncio
async def test_collection_fetcher_state_saving(mock_collection_page, tmp_path):
    """Test that state is saved periodically."""
    # Create mock client
    mock_client = AsyncMock(spec=DiscogsClient)
    mock_client.get_collection_page = AsyncMock(return_value=mock_collection_page)

    async def mock_get_all(*args, **kwargs):
        for release in mock_collection_page.releases:
            yield release

    mock_client.get_collection_all = mock_get_all

    # Create fetcher with small save interval
    fetcher = CollectionFetcher(
        mock_client,
        "testuser",
        save_interval_items=5,  # Save every 5 items
    )

    # Fetch all
    releases = await fetcher.fetch_all()

    # Verify state was updated
    assert fetcher.state.fetched_items == 10
    assert fetcher.state.total_items == 10
