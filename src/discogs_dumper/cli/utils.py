"""CLI utility functions.

Provides helper functions for Click commands, including async/await
integration and common CLI patterns.
"""

import asyncio
import functools
from typing import Any, Callable, TypeVar

import click

F = TypeVar("F", bound=Callable[..., Any])


def async_command(f: F) -> F:
    """Decorator to enable async functions as Click commands.

    Wraps an async function so it can be used as a Click command
    by running it with asyncio.run().

    Args:
        f: Async function to wrap

    Returns:
        Wrapped sync function for Click

    Examples:
        >>> @click.command()
        >>> @async_command
        >>> async def my_command():
        ...     await some_async_function()
    """

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))

    return wrapper  # type: ignore


def confirm_or_exit(message: str, default: bool = False) -> None:
    """Prompt for confirmation or exit.

    Args:
        message: Confirmation message
        default: Default value if user just presses enter

    Raises:
        click.Abort: If user declines
    """
    if not click.confirm(message, default=default):
        raise click.Abort()


def success(message: str) -> None:
    """Print success message in green.

    Args:
        message: Success message to display
    """
    click.secho(f"✓ {message}", fg="green")


def error(message: str) -> None:
    """Print error message in red.

    Args:
        message: Error message to display
    """
    click.secho(f"✗ {message}", fg="red", err=True)


def warning(message: str) -> None:
    """Print warning message in yellow.

    Args:
        message: Warning message to display
    """
    click.secho(f"⚠ {message}", fg="yellow")


def info(message: str) -> None:
    """Print info message in cyan.

    Args:
        message: Info message to display
    """
    click.secho(f"ℹ {message}", fg="cyan")
