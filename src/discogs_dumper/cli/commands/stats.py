"""Statistics command.

Display collection statistics including value, summary, and top items.
"""

import click
from loguru import logger

from discogs_dumper.cli.utils import async_command, error, info
from discogs_dumper.core.statistics import fetch_and_display_stats
from discogs_dumper.persistence.credentials import CredentialManager


@click.command()
@click.option(
    "--top-artists",
    is_flag=True,
    help="Show top artists by release count",
)
@click.option(
    "--top-labels",
    is_flag=True,
    help="Show top labels by release count",
)
@click.option(
    "--top-n",
    type=int,
    default=10,
    help="Number of top items to show (default: 10)",
)
@async_command
async def stats(
    top_artists: bool,
    top_labels: bool,
    top_n: int,
) -> None:
    """Display collection statistics.

    Shows collection value, summary statistics, and optionally
    top artists and labels.

    Examples:

        # Show collection value and summary
        discogs-dumper stats

        # Show top 5 artists
        discogs-dumper stats --top-artists --top-n 5

        # Show everything
        discogs-dumper stats --top-artists --top-labels
    """
    click.echo()

    # Check credentials
    if not CredentialManager.has_credentials():
        error("Not logged in")
        info("Run 'discogs-dumper auth login' first")
        click.echo()
        raise click.Abort()

    # Load credentials
    credentials = CredentialManager.load_credentials()
    if not credentials:
        error("Failed to load credentials")
        raise click.Abort()

    username, token = credentials

    try:
        await fetch_and_display_stats(
            username=username,
            token=token,
            show_value=True,
            show_summary=True,
            show_top_artists=top_artists,
            show_top_labels=top_labels,
            top_n=top_n,
        )

    except Exception as e:
        logger.error(f"Failed to fetch statistics: {e}")
        error(f"Failed to fetch statistics: {e}")
        raise click.Abort()
