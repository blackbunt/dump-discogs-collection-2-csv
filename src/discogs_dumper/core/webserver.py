"""HTTP server for serving QR code images.

Provides a simple HTTP server to serve QR code images for embedding
in Excel files as clickable links.
"""

import http.server
import socketserver
import threading
from pathlib import Path

from loguru import logger

from discogs_dumper.config.settings import settings


class QRWebServer:
    """Simple HTTP server for serving QR code images.

    Serves QR code images from a directory on a local port, allowing
    them to be referenced in Excel files as clickable links.

    Attributes:
        directory: Directory containing QR code images
        port: Port to serve on
        host: Host to bind to
        server: HTTP server instance
        thread: Server thread

    Examples:
        >>> server = QRWebServer()
        >>> server.start()
        >>> print(f"Server running at {server.url}")
        >>> # ... do work ...
        >>> server.stop()
    """

    def __init__(
        self,
        directory: Path | str | None = None,
        *,
        port: int | None = None,
        host: str | None = None,
    ) -> None:
        """Initialize QR web server.

        Args:
            directory: Directory to serve files from (default: qr/ from settings)
            port: Port to serve on (default: from settings)
            host: Host to bind to (default: from settings)
        """
        self.directory = Path(directory) if directory else settings.qr_output_path
        self.port = port if port is not None else settings.webserver_port
        self.host = host or settings.webserver_host

        self.server: socketserver.TCPServer | None = None
        self.thread: threading.Thread | None = None

        # Ensure directory exists
        self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def url(self) -> str:
        """Get server URL.

        Returns:
            Full URL to server (e.g., http://localhost:1224)

        Examples:
            >>> print(server.url)
            http://localhost:1224
        """
        return f"http://{self.host}:{self.port}"

    @property
    def is_running(self) -> bool:
        """Check if server is running.

        Returns:
            True if server is running, False otherwise
        """
        return self.server is not None and self.thread is not None

    def start(self) -> None:
        """Start the HTTP server in a background thread.

        Raises:
            RuntimeError: If server is already running

        Examples:
            >>> server.start()
            >>> print(f"Server started at {server.url}")
        """
        if self.is_running:
            raise RuntimeError("Server is already running")

        # Create request handler class with directory
        handler_class = create_handler_class(self.directory)

        # Create server
        try:
            self.server = socketserver.TCPServer(
                (self.host, self.port),
                handler_class,
            )
            self.server.allow_reuse_address = True

            # Start server in background thread
            self.thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
                name="QRWebServer",
            )
            self.thread.start()

            logger.info(f"QR web server started at {self.url}")
            logger.info(f"Serving files from {self.directory}")

        except OSError as e:
            logger.error(f"Failed to start server on {self.host}:{self.port}: {e}")
            raise

    def stop(self) -> None:
        """Stop the HTTP server.

        Examples:
            >>> server.stop()
            >>> print("Server stopped")
        """
        if not self.is_running:
            logger.warning("Server is not running")
            return

        if self.server:
            logger.info("Stopping QR web server...")
            self.server.shutdown()
            self.server.server_close()
            self.server = None

        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None

        logger.info("QR web server stopped")

    def __enter__(self) -> "QRWebServer":
        """Context manager entry.

        Examples:
            >>> with QRWebServer() as server:
            ...     print(f"Server at {server.url}")
        """
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit."""
        self.stop()


def create_handler_class(
    directory: Path,
) -> type[http.server.SimpleHTTPRequestHandler]:
    """Create HTTP request handler class for directory.

    Args:
        directory: Directory to serve files from

    Returns:
        Handler class configured for directory
    """

    class QRRequestHandler(http.server.SimpleHTTPRequestHandler):
        """Custom request handler for QR codes."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            """Initialize handler with custom directory."""
            super().__init__(*args, directory=str(directory), **kwargs)  # type: ignore

        def log_message(self, format: str, *args: object) -> None:
            """Override to use loguru instead of print.

            Args:
                format: Log message format string
                *args: Format arguments
            """
            logger.debug(f"{self.address_string()} - {format % args}")

    return QRRequestHandler


def serve_qr_codes(
    directory: Path | str | None = None,
    *,
    port: int | None = None,
    host: str | None = None,
    block: bool = True,
) -> QRWebServer:
    """Convenience function to start QR web server.

    Args:
        directory: Directory to serve files from (default: from settings)
        port: Port to serve on (default: from settings)
        host: Host to bind to (default: from settings)
        block: Block until interrupted if True (default: True)

    Returns:
        QRWebServer instance

    Examples:
        >>> # Non-blocking
        >>> server = serve_qr_codes(block=False)
        >>> # ... do work ...
        >>> server.stop()

        >>> # Blocking (runs until Ctrl+C)
        >>> serve_qr_codes(block=True)
    """
    server = QRWebServer(directory=directory, port=port, host=host)
    server.start()

    if block:
        try:
            logger.info("Server running. Press Ctrl+C to stop.")
            # Keep main thread alive
            import time

            while server.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            server.stop()

    return server
