"""Logging configuration using loguru.

Provides a simple interface for configuring application-wide logging
with sensible defaults and easy customization.
"""

import sys
from pathlib import Path
from typing import Any

from loguru import logger


def setup_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: Path | None = None,
    log_level: str | None = None,
) -> None:
    """Configure loguru logging for the application.

    Sets up console and optional file logging with appropriate formatting
    and log levels.

    Args:
        verbose: Enable debug-level logging (default: False)
        quiet: Suppress all output except errors (default: False)
        log_file: Optional path to log file for persistent logging
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Examples:
        >>> setup_logging()  # Default: INFO level to console
        >>> setup_logging(verbose=True)  # DEBUG level
        >>> setup_logging(quiet=True)  # Only errors
        >>> setup_logging(log_file=Path("app.log"))  # Also log to file
    """
    # Remove default handler
    logger.remove()

    # Determine console log level
    if log_level:
        console_level = log_level.upper()
    elif quiet:
        console_level = "ERROR"
    elif verbose:
        console_level = "DEBUG"
    else:
        console_level = "INFO"

    # Console handler with color and formatting
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=console_format,
        level=console_level,
        colorize=True,
    )

    # File handler if requested
    if log_file:
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # More detailed format for file logging
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        )

        logger.add(
            log_file,
            format=file_format,
            level="DEBUG",  # Always debug level for file
            rotation="10 MB",  # Rotate when file reaches 10MB
            retention="7 days",  # Keep logs for 7 days
            compression="zip",  # Compress rotated logs
        )

        logger.info(f"Logging to file: {log_file}")


def setup_quiet_logging() -> None:
    """Configure logging for quiet mode (errors only).

    Convenience function for setup_logging(quiet=True).
    """
    setup_logging(quiet=True)


def setup_verbose_logging() -> None:
    """Configure logging for verbose mode (debug level).

    Convenience function for setup_logging(verbose=True).
    """
    setup_logging(verbose=True)


def disable_logging() -> None:
    """Disable all logging output.

    Useful for testing or when running in non-interactive mode.
    """
    logger.remove()
    logger.add(sys.stderr, level="CRITICAL")  # Only critical errors


def get_logger(name: str | None = None) -> Any:
    """Get a logger instance.

    Args:
        name: Optional name for the logger (for filtering/identification)

    Returns:
        Loguru logger instance

    Note:
        Loguru uses a single global logger, so this mainly exists
        for API compatibility with standard logging.
    """
    if name:
        return logger.bind(name=name)
    return logger


# Configure logging on module import with sensible defaults
# This can be overridden by calling setup_logging() explicitly
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)
