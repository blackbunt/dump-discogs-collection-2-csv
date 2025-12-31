"""Credential management using OS keyring.

Provides secure storage and retrieval of Discogs API credentials
using the operating system's native keyring service:
- Linux: Secret Service (GNOME Keyring, KWallet)
- macOS: Keychain
- Windows: Credential Manager
"""

from typing import Final

import keyring
from loguru import logger

from discogs_dumper.persistence.models import CredentialInfo


class CredentialManager:
    """Manager for securely storing and retrieving API credentials.

    Uses the OS native keyring to store credentials securely,
    replacing the old plaintext YAML storage.
    """

    SERVICE_NAME: Final[str] = "discogs-dumper"
    USERNAME_KEY: Final[str] = "username"
    TOKEN_KEY: Final[str] = "token"

    @classmethod
    def save_credentials(cls, username: str, token: str) -> None:
        """Save credentials to OS keyring.

        Args:
            username: Discogs username
            token: Discogs API token

        Raises:
            keyring.errors.KeyringError: If keyring access fails
        """
        try:
            # Store username and token separately in keyring
            keyring.set_password(cls.SERVICE_NAME, cls.USERNAME_KEY, username)
            keyring.set_password(cls.SERVICE_NAME, cls.TOKEN_KEY, token)

            logger.info(f"Credentials saved securely for user: {username}")
            logger.debug(f"Token length: {len(token)} characters")

        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            raise

    @classmethod
    def load_credentials(cls) -> tuple[str, str] | None:
        """Load credentials from OS keyring.

        Returns:
            Tuple of (username, token) if found, None otherwise.

        Raises:
            keyring.errors.KeyringError: If keyring access fails
        """
        try:
            username = keyring.get_password(cls.SERVICE_NAME, cls.USERNAME_KEY)
            token = keyring.get_password(cls.SERVICE_NAME, cls.TOKEN_KEY)

            if username and token:
                logger.debug(f"Credentials loaded for user: {username}")
                return (username, token)

            logger.debug("No credentials found in keyring")
            return None

        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise

    @classmethod
    def delete_credentials(cls) -> bool:
        """Delete credentials from OS keyring.

        Returns:
            True if credentials were deleted, False if no credentials found.

        Raises:
            keyring.errors.KeyringError: If keyring access fails
        """
        try:
            username = keyring.get_password(cls.SERVICE_NAME, cls.USERNAME_KEY)

            if not username:
                logger.debug("No credentials to delete")
                return False

            # Delete both username and token
            keyring.delete_password(cls.SERVICE_NAME, cls.USERNAME_KEY)
            keyring.delete_password(cls.SERVICE_NAME, cls.TOKEN_KEY)

            logger.info(f"Credentials deleted for user: {username}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")
            raise

    @classmethod
    def has_credentials(cls) -> bool:
        """Check if credentials exist in keyring.

        Returns:
            True if credentials are stored, False otherwise.
        """
        try:
            username = keyring.get_password(cls.SERVICE_NAME, cls.USERNAME_KEY)
            token = keyring.get_password(cls.SERVICE_NAME, cls.TOKEN_KEY)
            return bool(username and token)
        except Exception:
            return False

    @classmethod
    def get_credential_info(cls) -> CredentialInfo | None:
        """Get credential information (without exposing the full token).

        Returns:
            CredentialInfo object with masked token, or None if no credentials.
        """
        creds = cls.load_credentials()
        if not creds:
            return None

        username, token = creds
        return CredentialInfo.from_credentials(username, token)

    @classmethod
    def update_token(cls, new_token: str) -> None:
        """Update only the API token, keeping the same username.

        Args:
            new_token: New Discogs API token

        Raises:
            ValueError: If no existing credentials found
            keyring.errors.KeyringError: If keyring access fails
        """
        username = keyring.get_password(cls.SERVICE_NAME, cls.USERNAME_KEY)

        if not username:
            raise ValueError("No existing credentials found. Use save_credentials() instead.")

        keyring.set_password(cls.SERVICE_NAME, cls.TOKEN_KEY, new_token)
        logger.info(f"Token updated for user: {username}")

    @classmethod
    def update_username(cls, new_username: str) -> None:
        """Update only the username, keeping the same token.

        Args:
            new_username: New Discogs username

        Raises:
            ValueError: If no existing credentials found
            keyring.errors.KeyringError: If keyring access fails
        """
        token = keyring.get_password(cls.SERVICE_NAME, cls.TOKEN_KEY)

        if not token:
            raise ValueError("No existing credentials found. Use save_credentials() instead.")

        # Delete old username entry
        old_username = keyring.get_password(cls.SERVICE_NAME, cls.USERNAME_KEY)
        if old_username:
            keyring.delete_password(cls.SERVICE_NAME, cls.USERNAME_KEY)

        # Save new username
        keyring.set_password(cls.SERVICE_NAME, cls.USERNAME_KEY, new_username)
        logger.info(f"Username updated: {old_username} -> {new_username}")


# Convenience functions for simple usage
def save_credentials(username: str, token: str) -> None:
    """Save credentials to OS keyring.

    Convenience wrapper around CredentialManager.save_credentials().

    Args:
        username: Discogs username
        token: Discogs API token
    """
    CredentialManager.save_credentials(username, token)


def load_credentials() -> tuple[str, str] | None:
    """Load credentials from OS keyring.

    Convenience wrapper around CredentialManager.load_credentials().

    Returns:
        Tuple of (username, token) if found, None otherwise.
    """
    return CredentialManager.load_credentials()


def delete_credentials() -> bool:
    """Delete credentials from OS keyring.

    Convenience wrapper around CredentialManager.delete_credentials().

    Returns:
        True if credentials were deleted, False if no credentials found.
    """
    return CredentialManager.delete_credentials()


def has_credentials() -> bool:
    """Check if credentials exist in keyring.

    Convenience wrapper around CredentialManager.has_credentials().

    Returns:
        True if credentials are stored, False otherwise.
    """
    return CredentialManager.has_credentials()
