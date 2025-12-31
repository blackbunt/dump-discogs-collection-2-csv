"""Pytest configuration and fixtures for discogs-dumper tests."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel


# Test data fixtures
@pytest.fixture
def sample_artist_data() -> dict[str, Any]:
    """Sample artist data from Discogs API."""
    return {
        "id": 123456,
        "name": "Test Artist",
        "resource_url": "https://api.discogs.com/artists/123456",
    }


@pytest.fixture
def sample_label_data() -> dict[str, Any]:
    """Sample label data from Discogs API."""
    return {
        "name": "Test Label",
        "catno": "TEST001",
    }


@pytest.fixture
def sample_basic_information() -> dict[str, Any]:
    """Sample basic_information from Discogs API release."""
    return {
        "id": 789012,
        "title": "Test Album",
        "year": 2024,
        "artists": [
            {
                "id": 123456,
                "name": "Test Artist",
                "resource_url": "https://api.discogs.com/artists/123456",
            }
        ],
        "labels": [{"name": "Test Label", "catno": "TEST001"}],
        "formats": [{"name": "Vinyl", "qty": "1", "descriptions": ["LP", "Album"]}],
        "styles": ["Rock", "Alternative"],
        "genres": ["Rock"],
        "thumb": "https://example.com/thumb.jpg",
        "cover_image": "https://example.com/cover.jpg",
    }


@pytest.fixture
def sample_release_data(sample_basic_information: dict[str, Any]) -> dict[str, Any]:
    """Sample release data from Discogs API."""
    return {
        "id": 789012,
        "instance_id": 999888,
        "date_added": "2024-01-15T10:30:00-08:00",
        "rating": 5,
        "basic_information": sample_basic_information,
        "notes": [],
    }


@pytest.fixture
def sample_collection_page(sample_release_data: dict[str, Any]) -> dict[str, Any]:
    """Sample collection page response from Discogs API."""
    return {
        "pagination": {"page": 1, "pages": 3, "per_page": 100, "items": 250},
        "releases": [sample_release_data],
    }


@pytest.fixture
def sample_collection_value() -> dict[str, Any]:
    """Sample collection value response from Discogs API."""
    return {
        "minimum": "€1,234.56",
        "median": "€5,678.90",
        "maximum": "€12,345.67",
    }


# Mock fixtures
@pytest.fixture
def mock_aiohttp_session() -> AsyncMock:
    """Mock aiohttp.ClientSession for testing API client."""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"test": "data"})
    session.get = AsyncMock(return_value=response)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


@pytest.fixture
def mock_keyring(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Mock keyring module for credential storage tests."""
    storage: dict[str, str] = {}

    def mock_set_password(service: str, username: str, password: str) -> None:
        storage[f"{service}:{username}"] = password

    def mock_get_password(service: str, username: str) -> str | None:
        return storage.get(f"{service}:{username}")

    def mock_delete_password(service: str, username: str) -> None:
        key = f"{service}:{username}"
        if key in storage:
            del storage[key]

    monkeypatch.setattr("keyring.set_password", mock_set_password)
    monkeypatch.setattr("keyring.get_password", mock_get_password)
    monkeypatch.setattr("keyring.delete_password", mock_delete_password)

    return storage


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Temporary directory for config files."""
    config_dir = tmp_path / ".discogs-dumper"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def sample_progress_state() -> dict[str, Any]:
    """Sample progress state for persistence tests."""
    return {
        "username": "testuser",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_items": 500,
        "fetched_items": 250,
        "downloaded_covers": [123, 456, 789],
        "generated_qrs": [123, 456],
    }


# Helper functions
@pytest.fixture
def make_temp_file(tmp_path: Path):
    """Factory fixture for creating temporary files."""

    def _make_file(filename: str, content: str = "") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    return _make_file


# Async helper fixtures
@pytest.fixture
def event_loop_policy():
    """Set event loop policy for async tests."""
    import asyncio

    return asyncio.get_event_loop_policy()
