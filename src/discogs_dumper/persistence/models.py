"""Pydantic models for persistence layer.

These models define the structure for saving and loading application state,
including progress tracking for resumable operations.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, computed_field


class ProgressState(BaseModel):
    """State for tracking progress of collection operations.

    This allows resuming interrupted downloads/exports without
    starting from scratch.
    """

    username: str
    started_at: datetime
    last_updated: datetime
    total_items: int
    fetched_items: int = 0
    downloaded_covers: list[int] = Field(default_factory=list)
    generated_qrs: list[int] = Field(default_factory=list)
    version: str = "2.0.0"

    @classmethod
    def create_new(cls, username: str, total_items: int) -> "ProgressState":
        """Create a new progress state.

        Args:
            username: Discogs username
            total_items: Total number of items in collection

        Returns:
            New ProgressState instance initialized with current time.
        """
        now = datetime.now(timezone.utc)
        return cls(
            username=username,
            started_at=now,
            last_updated=now,
            total_items=total_items,
        )

    def update_progress(
        self,
        fetched: int | None = None,
        cover_ids: list[int] | None = None,
        qr_ids: list[int] | None = None,
    ) -> None:
        """Update progress state.

        Args:
            fetched: Number of items fetched (optional)
            cover_ids: List of release IDs with downloaded covers (optional)
            qr_ids: List of release IDs with generated QR codes (optional)
        """
        if fetched is not None:
            self.fetched_items = fetched
        if cover_ids is not None:
            self.downloaded_covers = cover_ids
        if qr_ids is not None:
            self.generated_qrs = qr_ids
        self.last_updated = datetime.now(timezone.utc)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage.

        Returns:
            Progress as percentage (0-100).
        """
        if self.total_items == 0:
            return 100.0
        return (self.fetched_items / self.total_items) * 100

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_complete(self) -> bool:
        """Check if all items have been fetched.

        Returns:
            True if fetched_items equals total_items.
        """
        return self.fetched_items >= self.total_items

    @computed_field  # type: ignore[prop-decorator]
    @property
    def remaining_items(self) -> int:
        """Calculate remaining items to fetch.

        Returns:
            Number of items not yet fetched.
        """
        return max(0, self.total_items - self.fetched_items)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_seconds(self) -> float:
        """Calculate duration since start.

        Returns:
            Duration in seconds from started_at to last_updated.
        """
        delta = self.last_updated - self.started_at
        return delta.total_seconds()


class ExportJob(BaseModel):
    """Metadata for an export operation.

    Tracks details about collection exports for history/logging.
    """

    timestamp: datetime
    username: str
    format: Literal["excel", "csv"]
    output_path: str
    total_releases: int
    included_qr: bool
    included_covers: bool
    duration_seconds: float

    @classmethod
    def create(
        cls,
        username: str,
        format: Literal["excel", "csv"],
        output_path: str,
        total_releases: int,
        included_qr: bool = False,
        included_covers: bool = False,
    ) -> "ExportJob":
        """Create a new export job record.

        Args:
            username: Discogs username
            format: Export format (excel or csv)
            output_path: Path to output file
            total_releases: Number of releases exported
            included_qr: Whether QR codes were included
            included_covers: Whether cover art was included

        Returns:
            New ExportJob instance.
        """
        return cls(
            timestamp=datetime.now(timezone.utc),
            username=username,
            format=format,
            output_path=output_path,
            total_releases=total_releases,
            included_qr=included_qr,
            included_covers=included_covers,
            duration_seconds=0.0,
        )


class CredentialInfo(BaseModel):
    """Information about stored credentials (without exposing the token).

    Used for displaying authentication status to the user.
    """

    username: str
    token_length: int
    token_preview: str
    stored_at: datetime | None = None

    @classmethod
    def from_credentials(cls, username: str, token: str) -> "CredentialInfo":
        """Create credential info from actual credentials.

        Args:
            username: Discogs username
            token: API token (will be masked)

        Returns:
            CredentialInfo with masked token.
        """
        # Show first 4 and last 4 characters of token
        if len(token) > 8:
            preview = f"{token[:4]}...{token[-4:]}"
        else:
            preview = "***"

        return cls(
            username=username,
            token_length=len(token),
            token_preview=preview,
            stored_at=datetime.now(timezone.utc),
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def summary(self) -> str:
        """Get a summary string for display.

        Returns:
            Formatted credential summary.
        """
        return f"User: {self.username}, Token: {self.token_preview} ({self.token_length} chars)"
