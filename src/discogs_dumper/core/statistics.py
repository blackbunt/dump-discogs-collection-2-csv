"""Collection statistics and reporting.

Provides statistics about Discogs collections including value,
counts, and formatted display using Rich tables.
"""

from typing import Any

from loguru import logger
from rich.console import Console
from rich.table import Table

from discogs_dumper.api.client import DiscogsClient
from discogs_dumper.api.models import CollectionValue, Release


class CollectionStatistics:
    """Calculates and displays collection statistics.

    Provides methods to analyze collection data and display statistics
    in formatted tables using Rich.

    Examples:
        >>> stats = CollectionStatistics()
        >>> stats.display_value_info(value_info)
        >>> stats.display_collection_summary(releases)
    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize statistics calculator.

        Args:
            console: Rich console for output (creates new if None)
        """
        self.console = console or Console()

    def display_value_info(self, value_info: CollectionValue) -> None:
        """Display collection value information.

        Args:
            value_info: Collection value data from API

        Examples:
            >>> async with DiscogsClient(username, token) as client:
            ...     value_info = await client.get_collection_value()
            ...     stats.display_value_info(value_info)
        """
        table = Table(title="Collection Value", show_header=True, header_style="bold")

        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        # Total items
        table.add_row("Total Items", str(value_info.count))

        # Minimum value
        if value_info.minimum:
            min_val = f"${value_info.minimum:,.2f} ({value_info.median_currency})"
            table.add_row("Minimum Value", min_val)

        # Median value
        if value_info.median:
            median_val = f"${value_info.median:,.2f} ({value_info.median_currency})"
            table.add_row("Median Value", median_val)

        # Maximum value
        if value_info.maximum:
            max_val = f"${value_info.maximum:,.2f} ({value_info.median_currency})"
            table.add_row("Maximum Value", max_val)

        self.console.print()
        self.console.print(table)
        self.console.print()

    def display_collection_summary(self, releases: list[Release]) -> None:
        """Display summary statistics for collection.

        Args:
            releases: List of releases to analyze

        Examples:
            >>> stats.display_collection_summary(releases)
        """
        if not releases:
            self.console.print("[yellow]No releases to analyze[/yellow]")
            return

        table = Table(
            title="Collection Summary",
            show_header=True,
            header_style="bold",
        )

        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        # Total releases
        table.add_row("Total Releases", str(len(releases)))

        # Date range
        dates = [r.date_added for r in releases]
        oldest = min(dates)
        newest = max(dates)
        table.add_row("Oldest Added", oldest.strftime("%Y-%m-%d"))
        table.add_row("Newest Added", newest.strftime("%Y-%m-%d"))

        # Ratings
        rated = [r for r in releases if r.rating > 0]
        if rated:
            avg_rating = sum(r.rating for r in rated) / len(rated)
            table.add_row("Rated Releases", str(len(rated)))
            table.add_row("Average Rating", f"{avg_rating:.2f}")

        # Formats
        formats: dict[str, int] = {}
        for release in releases:
            for fmt in release.basic_information.formats:
                formats[fmt.name] = formats.get(fmt.name, 0) + 1

        if formats:
            top_format = max(formats, key=formats.get)  # type: ignore
            table.add_row("Unique Formats", str(len(formats)))
            table.add_row("Most Common Format", f"{top_format} ({formats[top_format]})")

        # Genres
        genres: dict[str, int] = {}
        for release in releases:
            for genre in release.basic_information.genres:
                genres[genre] = genres.get(genre, 0) + 1

        if genres:
            top_genre = max(genres, key=genres.get)  # type: ignore
            table.add_row("Unique Genres", str(len(genres)))
            table.add_row("Most Common Genre", f"{top_genre} ({genres[top_genre]})")

        self.console.print()
        self.console.print(table)
        self.console.print()

    def display_top_artists(
        self,
        releases: list[Release],
        top_n: int = 10,
    ) -> None:
        """Display top artists by release count.

        Args:
            releases: List of releases to analyze
            top_n: Number of top artists to show (default: 10)

        Examples:
            >>> stats.display_top_artists(releases, top_n=5)
        """
        if not releases:
            self.console.print("[yellow]No releases to analyze[/yellow]")
            return

        # Count releases per artist
        artist_counts: dict[str, int] = {}
        for release in releases:
            if release.basic_information.artists:
                artist = release.basic_information.artists[0].name
                artist_counts[artist] = artist_counts.get(artist, 0) + 1

        # Sort and take top N
        top_artists = sorted(
            artist_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_n]

        # Create table
        table = Table(
            title=f"Top {top_n} Artists",
            show_header=True,
            header_style="bold",
        )

        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Artist", style="magenta")
        table.add_column("Releases", style="green", justify="right")

        for rank, (artist, count) in enumerate(top_artists, 1):
            table.add_row(str(rank), artist, str(count))

        self.console.print()
        self.console.print(table)
        self.console.print()

    def display_top_labels(
        self,
        releases: list[Release],
        top_n: int = 10,
    ) -> None:
        """Display top labels by release count.

        Args:
            releases: List of releases to analyze
            top_n: Number of top labels to show (default: 10)

        Examples:
            >>> stats.display_top_labels(releases, top_n=5)
        """
        if not releases:
            self.console.print("[yellow]No releases to analyze[/yellow]")
            return

        # Count releases per label
        label_counts: dict[str, int] = {}
        for release in releases:
            if release.basic_information.labels:
                label = release.basic_information.labels[0].name
                label_counts[label] = label_counts.get(label, 0) + 1

        # Sort and take top N
        top_labels = sorted(
            label_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_n]

        # Create table
        table = Table(
            title=f"Top {top_n} Labels",
            show_header=True,
            header_style="bold",
        )

        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Label", style="magenta")
        table.add_column("Releases", style="green", justify="right")

        for rank, (label, count) in enumerate(top_labels, 1):
            table.add_row(str(rank), label, str(count))

        self.console.print()
        self.console.print(table)
        self.console.print()


async def fetch_and_display_stats(
    username: str,
    token: str,
    *,
    show_value: bool = True,
    show_summary: bool = True,
    show_top_artists: bool = False,
    show_top_labels: bool = False,
    top_n: int = 10,
) -> None:
    """Fetch collection and display statistics.

    Convenience function that fetches collection data and displays
    various statistics.

    Args:
        username: Discogs username
        token: Discogs API token
        show_value: Show collection value info (default: True)
        show_summary: Show collection summary (default: True)
        show_top_artists: Show top artists (default: False)
        show_top_labels: Show top labels (default: False)
        top_n: Number of top items to show (default: 10)

    Examples:
        >>> await fetch_and_display_stats(
        ...     "buntstift",
        ...     "my-token",
        ...     show_top_artists=True,
        ...     top_n=5
        ... )
    """
    stats = CollectionStatistics()

    async with DiscogsClient(username=username, token=token) as client:
        # Fetch value info
        if show_value:
            logger.info("Fetching collection value...")
            value_info = await client.get_collection_value()
            stats.display_value_info(value_info)

        # Fetch releases for other stats
        if show_summary or show_top_artists or show_top_labels:
            logger.info("Fetching collection releases...")
            releases: list[Release] = []

            async for release in client.get_collection_all():
                releases.append(release)

            if show_summary:
                stats.display_collection_summary(releases)

            if show_top_artists:
                stats.display_top_artists(releases, top_n=top_n)

            if show_top_labels:
                stats.display_top_labels(releases, top_n=top_n)
