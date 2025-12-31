"""Authentication commands.

Commands for managing Discogs API credentials using the system keyring.
"""

import click
from loguru import logger

from discogs_dumper.api.client import DiscogsClient
from discogs_dumper.cli.utils import async_command, error, info, success, warning
from discogs_dumper.persistence.credentials import CredentialManager


@click.group()
def auth() -> None:
    """Manage Discogs API authentication.

    Store, check, and remove your Discogs credentials securely
    using your system's keyring (Keychain on macOS, Secret Service
    on Linux, Credential Manager on Windows).
    """
    pass


@auth.command()
@async_command
async def login() -> None:
    """Login with Discogs credentials.

    Prompts for your Discogs username and API token, validates them
    by testing the connection, and stores them securely in your
    system keyring.

    To get your API token:
    1. Go to https://www.discogs.com/settings/developers
    2. Click "Generate new token"
    3. Copy the token

    Examples:
        discogs-dumper auth login
    """
    # Check if credentials already exist
    if CredentialManager.has_credentials():
        existing = CredentialManager.get_credential_info()
        if existing:
            warning(
                f"Credentials already exist for user '{existing.username}' "
                f"(stored {existing.stored_at})"
            )
            if not click.confirm("Overwrite existing credentials?", default=False):
                info("Login cancelled")
                return

    # Prompt for credentials
    click.echo()
    info("Enter your Discogs credentials")
    click.echo()

    username = click.prompt("Discogs Username", type=str)
    token = click.prompt(
        "Discogs API Token",
        type=str,
        hide_input=True,
    )

    click.echo()

    # Validate credentials by testing connection
    info("Validating credentials...")

    try:
        async with DiscogsClient(username=username, token=token) as client:
            is_valid = await client.test_connection()

            if not is_valid:
                error("Invalid credentials - authentication failed")
                raise click.Abort()

        # Save credentials
        CredentialManager.save_credentials(username=username, token=token)

        click.echo()
        success(f"Successfully logged in as '{username}'")
        info("Credentials stored securely in system keyring")
        click.echo()

    except Exception as e:
        logger.error(f"Login failed: {e}")
        error(f"Login failed: {e}")
        raise click.Abort()


@auth.command()
def logout() -> None:
    """Logout and remove stored credentials.

    Removes your Discogs credentials from the system keyring.

    Examples:
        discogs-dumper auth logout
    """
    if not CredentialManager.has_credentials():
        warning("No credentials found")
        return

    # Get info before deleting
    credential_info = CredentialManager.get_credential_info()

    # Confirm deletion
    if credential_info:
        click.echo()
        warning(f"This will delete credentials for user '{credential_info.username}'")
        if not click.confirm("Continue?", default=False):
            info("Logout cancelled")
            return

    # Delete credentials
    CredentialManager.delete_credentials()

    click.echo()
    success("Credentials deleted successfully")
    click.echo()


@auth.command()
def status() -> None:
    """Check authentication status.

    Displays information about currently stored credentials.

    Examples:
        discogs-dumper auth status
    """
    click.echo()

    if not CredentialManager.has_credentials():
        warning("Not logged in")
        info("Run 'discogs-dumper auth login' to authenticate")
        click.echo()
        return

    credential_info = CredentialManager.get_credential_info()

    if credential_info:
        success("Logged in")
        click.echo()
        click.echo(f"  Username:    {credential_info.username}")
        click.echo(f"  Token:       {credential_info.masked_token}")
        click.echo(f"  Stored at:   {credential_info.stored_at}")
        click.echo()
    else:
        error("Error reading credentials")
        click.echo()
