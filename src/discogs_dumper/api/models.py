"""Pydantic models for Discogs API responses.

These models define the structure of data returned by the Discogs API,
providing type safety and automatic validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, computed_field


class Artist(BaseModel):
    """Artist information from Discogs API."""

    id: int
    name: str
    resource_url: str


class Label(BaseModel):
    """Label information from Discogs API."""

    name: str
    catno: str


class Format(BaseModel):
    """Format information (Vinyl, CD, etc.) from Discogs API."""

    name: str
    qty: str
    descriptions: list[str] = Field(default_factory=list)


class BasicInformation(BaseModel):
    """Basic release information from Discogs API."""

    id: int
    title: str
    year: int
    artists: list[Artist]
    labels: list[Label]
    formats: list[Format]
    styles: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    thumb: str
    cover_image: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def primary_artist(self) -> str:
        """Get the primary artist name.

        Returns:
            Primary artist name, or "Unknown Artist" if no artists exist.
        """
        if self.artists:
            return self.artists[0].name
        return "Unknown Artist"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def primary_label(self) -> str:
        """Get the primary label name.

        Returns:
            Primary label name, or "Unknown Label" if no labels exist.
        """
        if self.labels:
            return self.labels[0].name
        return "Unknown Label"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def catalog_number(self) -> str:
        """Get the primary catalog number.

        Returns:
            Primary catalog number, or empty string if no labels exist.
        """
        if self.labels:
            return self.labels[0].catno
        return ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def format_description(self) -> str:
        """Get formatted string of formats.

        Returns:
            Comma-separated format names.
        """
        return ", ".join(f.name for f in self.formats)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def styles_str(self) -> str:
        """Get styles as comma-separated string.

        Returns:
            Comma-separated styles, or empty string if no styles.
        """
        return ", ".join(self.styles) if self.styles else ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def genres_str(self) -> str:
        """Get genres as comma-separated string.

        Returns:
            Comma-separated genres, or empty string if no genres.
        """
        return ", ".join(self.genres) if self.genres else ""


class Note(BaseModel):
    """Note field from Discogs release."""

    field_id: int
    value: str


class Release(BaseModel):
    """Complete release information from Discogs collection."""

    id: int
    instance_id: int
    date_added: datetime
    rating: int
    basic_information: BasicInformation
    notes: list[Note] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def discogs_webpage(self) -> str:
        """Get the Discogs release webpage URL.

        Returns:
            Full URL to the release page on discogs.com.
        """
        return f"https://www.discogs.com/release/{self.id}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def artist(self) -> str:
        """Get the primary artist name (shortcut).

        Returns:
            Primary artist name from basic_information.
        """
        return self.basic_information.primary_artist

    @computed_field  # type: ignore[prop-decorator]
    @property
    def album_title(self) -> str:
        """Get the album title (shortcut).

        Returns:
            Album title from basic_information.
        """
        return self.basic_information.title

    @computed_field  # type: ignore[prop-decorator]
    @property
    def year(self) -> int:
        """Get the release year (shortcut).

        Returns:
            Release year from basic_information.
        """
        return self.basic_information.year

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cover_url(self) -> str:
        """Get the full-size cover image URL.

        Returns:
            Cover image URL from basic_information.
        """
        return self.basic_information.cover_image

    @computed_field  # type: ignore[prop-decorator]
    @property
    def thumb_url(self) -> str:
        """Get the thumbnail cover image URL.

        Returns:
            Thumbnail URL from basic_information.
        """
        return self.basic_information.thumb

    @computed_field  # type: ignore[prop-decorator]
    @property
    def discogs_no(self) -> str:
        """Get the Discogs release ID as string.

        Returns:
            Release ID as string for compatibility with legacy code.
        """
        return str(self.id)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def notes_str(self) -> str:
        """Get all notes as a formatted string.

        Returns:
            Newline-separated note values, or empty string if no notes.
        """
        return "\n".join(note.value for note in self.notes) if self.notes else ""


class Pagination(BaseModel):
    """Pagination information from Discogs API."""

    page: int
    pages: int
    per_page: int
    items: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_next(self) -> bool:
        """Check if there are more pages.

        Returns:
            True if current page is not the last page.
        """
        return self.page < self.pages

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_last(self) -> bool:
        """Check if this is the last page.

        Returns:
            True if current page is the last page.
        """
        return self.page >= self.pages


class CollectionPage(BaseModel):
    """A single page of collection releases from Discogs API."""

    pagination: Pagination
    releases: list[Release]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def release_count(self) -> int:
        """Get the number of releases in this page.

        Returns:
            Number of releases in this page.
        """
        return len(self.releases)


class CollectionValue(BaseModel):
    """Collection value statistics from Discogs API.

    The Discogs API returns value information as formatted strings
    with currency symbols (e.g., "€1,234.56").
    """

    minimum: str = ""
    median: str = ""
    maximum: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def summary(self) -> str:
        """Get a formatted summary of collection value.

        Returns:
            Formatted string with min/median/max values.
        """
        return f"Min: {self.minimum}, Median: {self.median}, Max: {self.maximum}"


class ReleaseDetails(BaseModel):
    """Detailed release information (for future use).

    This model can be extended to include additional fields
    from the full release endpoint if needed.
    """

    id: int
    title: str
    artists: list[Artist]
    labels: list[Label]
    formats: list[Format]
    year: int
    genres: list[str] = Field(default_factory=list)
    styles: list[str] = Field(default_factory=list)
    tracklist: list[dict[str, Any]] = Field(default_factory=list)
    images: list[dict[str, Any]] = Field(default_factory=list)
