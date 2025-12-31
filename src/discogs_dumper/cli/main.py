"""Main CLI entry point.

Provides the main Click group and global options for the
discogs-dumper command-line interface.
"""

from pathlib import Path

import click

from discogs_dumper import __version__
from discogs_dumper.utils.logging import setup_logging


@click.group()
@click.version_option(version=__version__, prog_name="discogs-dumper")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress all output except errors",
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Write logs to file",
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    log_file: Path | None,
) -> None:
    """Discogs Collection Dumper - Export your Discogs collection.

    A modern tool for exporting your Discogs vinyl collection to Excel or CSV,
    with support for QR codes, cover art, and collection statistics.

    Examples:

        # First, login with your Discogs credentials
        discogs-dumper auth login

        # Export your collection to Excel
        discogs-dumper export --format excel

        # Export with QR codes and cover art
        discogs-dumper export --include-qr --include-cover

        # View collection statistics
        discogs-dumper stats

        # Generate QR codes
        discogs-dumper qr generate

    For more information on a specific command, run:
        discogs-dumper COMMAND --help
    """
    # Setup logging based on global options
    setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


# Import and register command groups
# These imports must come after the cli group is defined
from discogs_dumper.cli.commands import (  # noqa: E402
    auth,
    cover,
    export,
    qr,
    server,
    stats,
)

cli.add_command(auth.auth)
cli.add_command(export.export)
cli.add_command(stats.stats)
cli.add_command(qr.qr)
cli.add_command(cover.cover)
cli.add_command(server.server)


if __name__ == "__main__":
    cli()
