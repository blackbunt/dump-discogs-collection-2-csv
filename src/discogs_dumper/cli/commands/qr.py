"""QR code commands.

Generate QR codes for collection releases.
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
from discogs_dumper.core.qr_generator import QRGenerator
from discogs_dumper.persistence.credentials import CredentialManager


@click.group()
def qr() -> None:
    """QR code management.

    Generate QR codes containing Discogs URLs for your collection.
    """
    pass


@qr.command()
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for QR codes (default: qr/)",
)
@click.option(
    "--skip-existing/--overwrite",
    default=True,
    help="Skip existing QR codes (default: skip)",
)
@async_command
async def generate(
    output_dir: Path | None,
    skip_existing: bool,
) -> None:
    """Generate QR codes for collection.

    Creates PNG QR codes containing Discogs URLs for each release
    in your collection.

    Examples:

        # Generate QR codes to default directory (qr/)
        discogs-dumper qr generate

        # Generate to custom directory
        discogs-dumper qr generate --output-dir my-qr-codes/

        # Overwrite existing QR codes
        discogs-dumper qr generate --overwrite
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

            # Generate QR codes
            task_qr = progress.add_task(
                "[cyan]Generating QR codes...",
                total=len(releases),
            )

            qr_generator = QRGenerator(output_dir=output_dir)

            async def qr_progress(current: int, total: int) -> None:
                progress.update(
                    task_qr,
                    completed=current,
                    total=total,
                    description=f"[cyan]Generating QR codes ({current}/{total})...",
                )

            qr_paths = await qr_generator.generate_for_releases(
                releases,
                skip_existing=skip_existing,
                progress_callback=qr_progress,
            )

            progress.update(
                task_qr,
                description=f"[green]✓ Generated {len(qr_paths)} QR codes",
            )

        click.echo()
        success(
            f"Generated {len(qr_paths)} QR codes "
            f"(skipped {len(releases) - len(qr_paths)})"
        )
        info(f"QR codes saved to: {qr_generator.output_dir}")
        click.echo()

    except Exception as e:
        logger.error(f"QR generation failed: {e}")
        error(f"QR generation failed: {e}")
        raise click.Abort()
