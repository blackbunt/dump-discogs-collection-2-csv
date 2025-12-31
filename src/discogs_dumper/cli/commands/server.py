"""Web server commands.

Start HTTP server for serving QR code images.
"""

from pathlib import Path

import click
from loguru import logger

from discogs_dumper.cli.utils import error, info, success
from discogs_dumper.core.webserver import serve_qr_codes


@click.group()
def server() -> None:
    """Web server management.

    Start HTTP server to serve QR code images for embedding
    in Excel files.
    """
    pass


@server.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(path_type=Path),
    help="Directory to serve QR codes from (default: qr/)",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=1224,
    help="Port to serve on (default: 1224)",
)
@click.option(
    "--host",
    "-h",
    default="localhost",
    help="Host to bind to (default: localhost)",
)
def start(
    directory: Path | None,
    port: int,
    host: str,
) -> None:
    """Start QR code web server.

    Starts an HTTP server to serve QR code images. This allows
    QR codes to be referenced as URLs in Excel files.

    The server runs until interrupted with Ctrl+C.

    Examples:

        # Start server with defaults (localhost:1224, qr/ directory)
        discogs-dumper server start

        # Start on custom port
        discogs-dumper server start --port 8080

        # Serve custom directory
        discogs-dumper server start --directory my-qr-codes/
    """
    click.echo()

    try:
        info(f"Starting web server on {host}:{port}")

        if directory:
            info(f"Serving files from: {directory}")

        click.echo()

        # Start server (blocks until Ctrl+C)
        serve_qr_codes(
            directory=directory,
            port=port,
            host=host,
            block=True,
        )

    except KeyboardInterrupt:
        click.echo()
        info("Server stopped by user")
        click.echo()

    except Exception as e:
        logger.error(f"Server failed: {e}")
        click.echo()
        error(f"Server failed: {e}")
        click.echo()
        raise click.Abort()
