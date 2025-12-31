"""Unit tests for state management."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from discogs_dumper.persistence.models import ProgressState
from discogs_dumper.persistence.state import StateManager


class TestStateManager:
    """Test suite for StateManager."""

    @pytest.fixture
    def temp_state_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        """Create temporary state directory."""
        state_dir = tmp_path / ".discogs-dumper"
        state_dir.mkdir(parents=True, exist_ok=True)

        # Monkey patch StateManager to use temp directory
        monkeypatch.setattr(StateManager, "STATE_DIR", state_dir)
        monkeypatch.setattr(StateManager, "STATE_FILE", state_dir / "progress.json")

        return state_dir

    def test_save_and_load_state(self, temp_state_dir: Path) -> None:
        """Test saving and loading state."""
        # Create state
        state = ProgressState.create_new("testuser", total_items=100)
        state.fetched_items = 50

        # Save
        StateManager.save_state(state)

        # Verify file exists
        assert StateManager.STATE_FILE.exists()

        # Load
        loaded = StateManager.load_state()

        assert loaded is not None
        assert loaded.username == "testuser"
        assert loaded.total_items == 100
        assert loaded.fetched_items == 50

    def test_load_state_not_found(self, temp_state_dir: Path) -> None:
        """Test loading when no state file exists."""
        loaded = StateManager.load_state()
        assert loaded is None

    def test_load_state_with_username_validation(self, temp_state_dir: Path) -> None:
        """Test loading with username validation."""
        # Save state for user1
        state = ProgressState.create_new("user1", total_items=100)
        StateManager.save_state(state)

        # Load with correct username
        loaded = StateManager.load_state("user1")
        assert loaded is not None
        assert loaded.username == "user1"

        # Load with wrong username
        loaded = StateManager.load_state("user2")
        assert loaded is None  # Should return None due to username mismatch

    def test_clear_state(self, temp_state_dir: Path) -> None:
        """Test clearing state."""
        # Save state
        state = ProgressState.create_new("testuser", total_items=100)
        StateManager.save_state(state)

        assert StateManager.STATE_FILE.exists()

        # Clear
        result = StateManager.clear_state()
        assert result is True
        assert not StateManager.STATE_FILE.exists()

    def test_clear_state_not_found(self, temp_state_dir: Path) -> None:
        """Test clearing when no state exists."""
        result = StateManager.clear_state()
        assert result is False

    def test_clear_state_with_username_validation(self, temp_state_dir: Path) -> None:
        """Test clearing with username validation."""
        # Save state for user1
        state = ProgressState.create_new("user1", total_items=100)
        StateManager.save_state(state)

        # Try to clear with wrong username
        result = StateManager.clear_state("user2")
        assert result is False
        assert StateManager.STATE_FILE.exists()  # Should still exist

        # Clear with correct username
        result = StateManager.clear_state("user1")
        assert result is True
        assert not StateManager.STATE_FILE.exists()

    def test_has_state(self, temp_state_dir: Path) -> None:
        """Test checking if state exists."""
        # Initially no state
        assert not StateManager.has_state()

        # Save state
        state = ProgressState.create_new("testuser", total_items=100)
        StateManager.save_state(state)

        # Now should have state
        assert StateManager.has_state()
        assert StateManager.has_state("testuser")
        assert not StateManager.has_state("otheruser")

    def test_update_state(self, temp_state_dir: Path) -> None:
        """Test updating existing state."""
        # Create initial state
        state = ProgressState.create_new("testuser", total_items=100)
        StateManager.save_state(state)

        # Update state
        updated = StateManager.update_state(
            username="testuser",
            fetched=50,
            cover_ids=[1, 2, 3],
            qr_ids=[1, 2],
        )

        assert updated.fetched_items == 50
        assert updated.downloaded_covers == [1, 2, 3]
        assert updated.generated_qrs == [1, 2]

        # Verify saved
        loaded = StateManager.load_state("testuser")
        assert loaded is not None
        assert loaded.fetched_items == 50

    def test_update_state_not_found(self, temp_state_dir: Path) -> None:
        """Test updating when no state exists."""
        with pytest.raises(ValueError, match="No existing state found"):
            StateManager.update_state(username="testuser", fetched=50)

    def test_get_or_create_state_creates_new(self, temp_state_dir: Path) -> None:
        """Test get_or_create when no state exists."""
        state = StateManager.get_or_create_state("testuser", total_items=100)

        assert state.username == "testuser"
        assert state.total_items == 100
        assert state.fetched_items == 0

        # Verify saved
        assert StateManager.has_state("testuser")

    def test_get_or_create_state_returns_existing(self, temp_state_dir: Path) -> None:
        """Test get_or_create when state already exists."""
        # Create initial state
        initial = ProgressState.create_new("testuser", total_items=100)
        initial.fetched_items = 50
        StateManager.save_state(initial)

        # Get or create should return existing
        state = StateManager.get_or_create_state("testuser", total_items=100)

        assert state.fetched_items == 50  # Should have existing progress

    def test_get_or_create_updates_total_items(self, temp_state_dir: Path) -> None:
        """Test that get_or_create updates total_items if changed."""
        # Create initial state
        initial = ProgressState.create_new("testuser", total_items=100)
        StateManager.save_state(initial)

        # Get with different total_items
        state = StateManager.get_or_create_state("testuser", total_items=150)

        assert state.total_items == 150  # Should be updated

        # Verify saved with new total
        loaded = StateManager.load_state("testuser")
        assert loaded is not None
        assert loaded.total_items == 150

    def test_load_invalid_json(self, temp_state_dir: Path) -> None:
        """Test loading corrupted JSON file."""
        # Write invalid JSON
        StateManager.STATE_FILE.write_text("{ invalid json }")

        loaded = StateManager.load_state()
        assert loaded is None

    def test_load_invalid_schema(self, temp_state_dir: Path) -> None:
        """Test loading JSON with invalid schema."""
        # Write JSON that doesn't match ProgressState schema
        StateManager.STATE_FILE.write_text('{"invalid": "schema"}')

        loaded = StateManager.load_state()
        assert loaded is None

    def test_state_persistence_preserves_types(self, temp_state_dir: Path) -> None:
        """Test that all field types are preserved through save/load."""
        # Create state with all fields populated
        state = ProgressState(
            username="testuser",
            started_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            total_items=500,
            fetched_items=250,
            downloaded_covers=[1, 2, 3, 4, 5],
            generated_qrs=[1, 2, 3],
            version="2.0.0",
        )

        StateManager.save_state(state)
        loaded = StateManager.load_state()

        assert loaded is not None
        assert loaded.username == state.username
        assert loaded.total_items == state.total_items
        assert loaded.fetched_items == state.fetched_items
        assert loaded.downloaded_covers == state.downloaded_covers
        assert loaded.generated_qrs == state.generated_qrs
        assert loaded.version == state.version
        # Datetimes should be close (within 1 second)
        assert abs((loaded.started_at - state.started_at).total_seconds()) < 1

    def test_progress_state_computed_fields(self) -> None:
        """Test ProgressState computed properties."""
        state = ProgressState.create_new("testuser", total_items=100)
        state.fetched_items = 50

        # Test computed fields
        assert state.progress_percentage == 50.0
        assert state.remaining_items == 50
        assert not state.is_complete

        # Complete state
        state.fetched_items = 100
        assert state.progress_percentage == 100.0
        assert state.remaining_items == 0
        assert state.is_complete

    def test_progress_state_update_method(self) -> None:
        """Test ProgressState.update_progress method."""
        state = ProgressState.create_new("testuser", total_items=100)

        # Update only fetched
        state.update_progress(fetched=50)
        assert state.fetched_items == 50

        # Update covers and qrs
        state.update_progress(cover_ids=[1, 2, 3], qr_ids=[1, 2])
        assert state.downloaded_covers == [1, 2, 3]
        assert state.generated_qrs == [1, 2]

        # Update all at once
        state.update_progress(fetched=75, cover_ids=[1, 2, 3, 4], qr_ids=[1, 2, 3])
        assert state.fetched_items == 75
        assert len(state.downloaded_covers) == 4
        assert len(state.generated_qrs) == 3
