"""State management for resumable operations.

Provides persistence for progress tracking, allowing interrupted
downloads and exports to be resumed from where they left off.
"""

import json
from pathlib import Path
from typing import Final

from loguru import logger
from pydantic import ValidationError

from discogs_dumper.persistence.models import ProgressState


class StateManager:
    """Manager for saving and loading progress state.

    Stores progress information in JSON format at:
    ~/.discogs-dumper/progress.json

    This allows resuming interrupted operations without starting over.
    """

    STATE_DIR: Final[Path] = Path.home() / ".discogs-dumper"
    STATE_FILE: Final[Path] = STATE_DIR / "progress.json"

    @classmethod
    def _ensure_state_dir(cls) -> None:
        """Ensure state directory exists."""
        cls.STATE_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"State directory: {cls.STATE_DIR}")

    @classmethod
    def save_state(cls, state: ProgressState) -> None:
        """Save progress state to JSON file.

        Args:
            state: ProgressState object to save

        Raises:
            OSError: If file cannot be written
        """
        cls._ensure_state_dir()

        try:
            # Convert Pydantic model to JSON
            state_dict = state.model_dump(mode="json")

            # Write to file with pretty formatting
            with open(cls.STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)

            logger.debug(
                f"State saved: {state.fetched_items}/{state.total_items} items "
                f"({state.progress_percentage:.1f}%)"
            )

        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise

    @classmethod
    def load_state(cls, username: str | None = None) -> ProgressState | None:
        """Load progress state from JSON file.

        Args:
            username: Optional username to validate state belongs to correct user

        Returns:
            ProgressState if found and valid, None otherwise.

        Raises:
            ValidationError: If state file is corrupted
        """
        if not cls.STATE_FILE.exists():
            logger.debug("No state file found")
            return None

        try:
            with open(cls.STATE_FILE, "r", encoding="utf-8") as f:
                state_dict = json.load(f)

            # Validate and parse with Pydantic
            state = ProgressState.model_validate(state_dict)

            # Check if state belongs to requested user
            if username and state.username != username:
                logger.warning(
                    f"State file is for user '{state.username}', "
                    f"but requested user is '{username}'. Ignoring state."
                )
                return None

            logger.info(
                f"State loaded: {state.fetched_items}/{state.total_items} items "
                f"({state.progress_percentage:.1f}% complete)"
            )

            return state

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in state file: {e}")
            return None

        except ValidationError as e:
            logger.error(f"Invalid state file format: {e}")
            return None

        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None

    @classmethod
    def clear_state(cls, username: str | None = None) -> bool:
        """Clear saved progress state.

        Args:
            username: Optional username to verify before clearing

        Returns:
            True if state was cleared, False if no state found or username mismatch.
        """
        if not cls.STATE_FILE.exists():
            logger.debug("No state file to clear")
            return False

        # If username specified, verify it matches before deleting
        if username:
            state = cls.load_state(username)
            if not state or state.username != username:
                logger.warning(
                    f"State file is for different user, not clearing"
                )
                return False

        try:
            cls.STATE_FILE.unlink()
            logger.info("Progress state cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear state: {e}")
            raise

    @classmethod
    def has_state(cls, username: str | None = None) -> bool:
        """Check if progress state exists.

        Args:
            username: Optional username to verify state belongs to user

        Returns:
            True if valid state exists for the user.
        """
        if not cls.STATE_FILE.exists():
            return False

        if username:
            state = cls.load_state(username)
            return state is not None and state.username == username

        return True

    @classmethod
    def update_state(
        cls,
        username: str,
        fetched: int | None = None,
        cover_ids: list[int] | None = None,
        qr_ids: list[int] | None = None,
    ) -> ProgressState:
        """Update existing state or create new one.

        This is a convenience method that loads existing state,
        updates it, and saves it back.

        Args:
            username: Discogs username
            fetched: Number of items fetched (optional)
            cover_ids: List of release IDs with downloaded covers (optional)
            qr_ids: List of release IDs with generated QR codes (optional)

        Returns:
            Updated ProgressState object.

        Raises:
            ValueError: If no existing state found
        """
        state = cls.load_state(username)

        if not state:
            raise ValueError(
                f"No existing state found for user '{username}'. "
                "Create initial state first."
            )

        # Update the state
        state.update_progress(fetched=fetched, cover_ids=cover_ids, qr_ids=qr_ids)

        # Save updated state
        cls.save_state(state)

        return state

    @classmethod
    def get_or_create_state(
        cls,
        username: str,
        total_items: int,
    ) -> ProgressState:
        """Get existing state or create new one if not found.

        Args:
            username: Discogs username
            total_items: Total number of items in collection

        Returns:
            Existing or newly created ProgressState.
        """
        state = cls.load_state(username)

        if state:
            # Update total_items if changed
            if state.total_items != total_items:
                logger.info(
                    f"Collection size changed: {state.total_items} -> {total_items}"
                )
                state.total_items = total_items
                cls.save_state(state)

            return state

        # Create new state
        logger.info(f"Creating new progress state for {username}")
        state = ProgressState.create_new(username, total_items)
        cls.save_state(state)

        return state


# Convenience functions
def save_state(state: ProgressState) -> None:
    """Save progress state.

    Convenience wrapper around StateManager.save_state().

    Args:
        state: ProgressState to save
    """
    StateManager.save_state(state)


def load_state(username: str | None = None) -> ProgressState | None:
    """Load progress state.

    Convenience wrapper around StateManager.load_state().

    Args:
        username: Optional username to validate

    Returns:
        ProgressState if found, None otherwise.
    """
    return StateManager.load_state(username)


def clear_state(username: str | None = None) -> bool:
    """Clear progress state.

    Convenience wrapper around StateManager.clear_state().

    Args:
        username: Optional username to verify

    Returns:
        True if state was cleared, False otherwise.
    """
    return StateManager.clear_state(username)


def has_state(username: str | None = None) -> bool:
    """Check if progress state exists.

    Convenience wrapper around StateManager.has_state().

    Args:
        username: Optional username to verify

    Returns:
        True if state exists for user.
    """
    return StateManager.has_state(username)
