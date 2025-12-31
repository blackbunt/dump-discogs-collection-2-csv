"""Export command.

Main command for exporting Discogs collection to Excel or CSV,
with optional QR code and cover art download.
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
from discogs_dumper.cli.utils import async_command, error, info, success, warning
from discogs_dumper.core.collection import CollectionFetcher
from discogs_dumper.core.cover_downloader import CoverDownloader
from discogs_dumper.core.exporter import CollectionExporter
from discogs_dumper.core.qr_generator import QRGenerator
from discogs_dumper.core.webserver import QRWebServer
from discogs_dumper.persistence.credentials import CredentialManager


@click.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["excel", "csv"], case_sensitive=False),
    default="excel",
    help="Export format (default: excel)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: discogs_collection.xlsx or .csv)",
)
@click.option(
    "--include-qr/--no-qr",
    default=False,
    help="Generate QR codes and include QR URL column (default: no)",
)
@click.option(
    "--include-cover/--no-cover",
    default=False,
    help="Download cover art and include cover URL column (default: no)",
)
@click.option(
    "--resume/--no-resume",
    default=False,
    help="Resume from previous incomplete export (default: no)",
)
@click.option(
    "--qr-port",
    type=int,
    default=1224,
    help="Port for QR code web server (default: 1224)",
)
@async_command
async def export(
    format: str,
    output: Path | None,
    include_qr: bool,
    include_cover: bool,
    resume: bool,
    qr_port: int,
) -> None:
    """Export your Discogs collection.

    Fetches your collection from Discogs and exports it to Excel or CSV format.
    Optionally generates QR codes and downloads cover art.

    Examples:

        # Basic export to Excel
        discogs-dumper export

        # Export to CSV with custom filename
        discogs-dumper export --format csv --output my_collection.csv

        # Export with QR codes and cover art
        discogs-dumper export --include-qr --include-cover

        # Resume interrupted export
        discogs-dumper export --resume
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

    # Determine output path
    if output is None:
        extension = ".xlsx" if format == "excel" else ".csv"
        output = Path(f"discogs_collection{extension}")

    info(f"Exporting collection for user '{username}'")
    click.echo()

    try:
        # Start QR web server if needed
        qr_server: QRWebServer | None = None
        qr_server_url: str | None = None

        if include_qr:
            qr_server = QRWebServer(port=qr_port)
            qr_server.start()
            qr_server_url = qr_server.url
            info(f"QR web server started at {qr_server_url}")

        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        ) as progress:

            # Step 1: Fetch collection
            task_fetch = progress.add_task(
                "[cyan]Fetching collection...",
                total=100,
            )

            releases = []

            async with DiscogsClient(username=username, token=token) as client:
                fetcher = CollectionFetcher(client, username, resume=resume)

                async def fetch_progress(current: int, total: int) -> None:
                    progress.update(
                        task_fetch,
                        completed=current,
                        total=total,
                        description=f"[cyan]Fetching collection ({current}/{total})...",
                    )

                releases = await fetcher.fetch_all(progress_callback=fetch_progress)

            progress.update(
                task_fetch,
                description=f"[green]✓ Fetched {len(releases)} releases",
            )

            # Step 2: Generate QR codes (if requested)
            if include_qr:
                task_qr = progress.add_task(
                    "[cyan]Generating QR codes...",
                    total=len(releases),
                )

                qr_generator = QRGenerator()

                async def qr_progress(current: int, total: int) -> None:
                    progress.update(
                        task_qr,
                        completed=current,
                        total=total,
                        description=f"[cyan]Generating QR codes ({current}/{total})...",
                    )

                qr_paths = await qr_generator.generate_for_releases(
                    releases,
                    progress_callback=qr_progress,
                )

                progress.update(
                    task_qr,
                    description=f"[green]✓ Generated {len(qr_paths)} QR codes",
                )

            # Step 3: Download covers (if requested)
            if include_cover:
                task_cover = progress.add_task(
                    "[cyan]Downloading covers...",
                    total=len(releases),
                )

                cover_downloader = CoverDownloader()

                async def cover_progress(current: int, total: int) -> None:
                    progress.update(
                        task_cover,
                        completed=current,
                        total=total,
                        description=f"[cyan]Downloading covers ({current}/{total})...",
                    )

                cover_paths = await cover_downloader.download_for_releases(
                    releases,
                    progress_callback=cover_progress,
                )

                progress.update(
                    task_cover,
                    description=f"[green]✓ Downloaded {len(cover_paths)} covers",
                )

            # Step 4: Export to file
            task_export = progress.add_task(
                f"[cyan]Exporting to {format.upper()}...",
                total=None,
            )

            exporter = CollectionExporter()
            export_path = exporter.export(
                releases,
                output,
                format=format,
                include_qr_url=include_qr,
                include_cover_url=include_cover,
                qr_server_url=qr_server_url,
            )

            progress.update(
                task_export,
                description=f"[green]✓ Exported to {export_path.name}",
            )

        # Stop QR server
        if qr_server:
            qr_server.stop()

        click.echo()
        success(f"Export completed: {export_path}")

        if include_qr and qr_server_url:
            click.echo()
            info(f"QR codes can be accessed via web server at {qr_server_url}")
            info("To serve QR codes later, run: discogs-dumper server start")

        click.echo()

    except Exception as e:
        logger.error(f"Export failed: {e}")
        error(f"Export failed: {e}")

        # Stop QR server on error
        if qr_server:
            qr_server.stop()

        raise click.Abort()
