"""Cover art commands.

Download cover art for collection releases.
"""

from pathlib import Path

import click
from loguru import logger
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from discogs_dumper.api.client import DiscogsClient
from discogs_dumper.cli.utils import async_command, error, info, success
from discogs_dumper.core.cover_downloader import CoverDownloader
from discogs_dumper.persistence.credentials import CredentialManager


@click.group()
def cover() -> None:
    """Cover art management.

    Download cover art images for your collection.
    """
    pass


@cover.command()
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for covers (default: Cover-Art/)",
)
@click.option(
    "--skip-existing/--overwrite",
    default=True,
    help="Skip existing covers (default: skip)",
)
@async_command
async def download(
    output_dir: Path | None,
    skip_existing: bool,
) -> None:
    """Download cover art for collection.

    Downloads cover art images (JPG) for each release in your collection.

    Examples:

        # Download covers to default directory (Cover-Art/)
        discogs-dumper cover download

        # Download to custom directory
        discogs-dumper cover download --output-dir my-covers/

        # Overwrite existing covers
        discogs-dumper cover download --overwrite
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
        # Fetch collection
        info(f"Fetching collection for user '{username}'")

        releases = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        ) as progress:

            # Fetch releases
            task_fetch = progress.add_task(
                "[cyan]Fetching releases...",
                total=100,
            )

            async with DiscogsClient(username=username, token=token) as client:
                async for release in client.get_collection_all():
                    releases.append(release)
                    progress.update(task_fetch, completed=len(releases))

            progress.update(
                task_fetch,
                description=f"[green]✓ Fetched {len(releases)} releases",
                completed=len(releases),
            )

            # Download covers
            task_cover = progress.add_task(
                "[cyan]Downloading covers...",
                total=len(releases),
            )

            cover_downloader = CoverDownloader(output_dir=output_dir)

            async def cover_progress(current: int, total: int) -> None:
                progress.update(
                    task_cover,
                    completed=current,
                    total=total,
                    description=f"[cyan]Downloading covers ({current}/{total})...",
                )

            cover_paths = await cover_downloader.download_for_releases(
                releases,
                skip_existing=skip_existing,
                progress_callback=cover_progress,
            )

            progress.update(
                task_cover,
                description=f"[green]✓ Downloaded {len(cover_paths)} covers",
            )

        click.echo()
        success(
            f"Downloaded {len(cover_paths)} covers "
            f"(skipped/unavailable {len(releases) - len(cover_paths)})"
        )
        info(f"Covers saved to: {cover_downloader.output_dir}")
        click.echo()

    except Exception as e:
        logger.error(f"Cover download failed: {e}")
        error(f"Cover download failed: {e}")
        raise click.Abort()
