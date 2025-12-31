"""Unit tests for credential management."""

import pytest

from discogs_dumper.persistence.credentials import CredentialManager
from discogs_dumper.persistence.models import CredentialInfo


class TestCredentialManager:
    """Test suite for CredentialManager."""

    def test_save_and_load_credentials(self, mock_keyring: dict) -> None:
        """Test saving and loading credentials."""
        username = "testuser"
        token = "test_token_12345"

        # Save credentials
        CredentialManager.save_credentials(username, token)

        # Verify stored in mock keyring
        assert f"{CredentialManager.SERVICE_NAME}:{CredentialManager.USERNAME_KEY}" in mock_keyring
        assert f"{CredentialManager.SERVICE_NAME}:{CredentialManager.TOKEN_KEY}" in mock_keyring

        # Load credentials
        loaded = CredentialManager.load_credentials()

        assert loaded is not None
        assert loaded == (username, token)

    def test_load_credentials_not_found(self, mock_keyring: dict) -> None:
        """Test loading when no credentials exist."""
        loaded = CredentialManager.load_credentials()
        assert loaded is None

    def test_delete_credentials(self, mock_keyring: dict) -> None:
        """Test deleting credentials."""
        username = "testuser"
        token = "test_token_12345"

        # Save first
        CredentialManager.save_credentials(username, token)
        assert CredentialManager.has_credentials()

        # Delete
        result = CredentialManager.delete_credentials()
        assert result is True

        # Verify deleted
        assert not CredentialManager.has_credentials()
        loaded = CredentialManager.load_credentials()
        assert loaded is None

    def test_delete_credentials_not_found(self, mock_keyring: dict) -> None:
        """Test deleting when no credentials exist."""
        result = CredentialManager.delete_credentials()
        assert result is False

    def test_has_credentials(self, mock_keyring: dict) -> None:
        """Test checking if credentials exist."""
        # Initially no credentials
        assert not CredentialManager.has_credentials()

        # Save credentials
        CredentialManager.save_credentials("testuser", "token123")

        # Now should have credentials
        assert CredentialManager.has_credentials()

    def test_get_credential_info(self, mock_keyring: dict) -> None:
        """Test getting credential info with masked token."""
        username = "testuser"
        token = "very_long_secret_token_12345"

        # No credentials initially
        info = CredentialManager.get_credential_info()
        assert info is None

        # Save credentials
        CredentialManager.save_credentials(username, token)

        # Get info
        info = CredentialManager.get_credential_info()
        assert info is not None
        assert isinstance(info, CredentialInfo)
        assert info.username == username
        assert info.token_length == len(token)
        # Token should be masked
        assert token not in info.token_preview
        assert info.token_preview.startswith(token[:4])
        assert info.token_preview.endswith(token[-4:])

    def test_update_token(self, mock_keyring: dict) -> None:
        """Test updating only the token."""
        username = "testuser"
        old_token = "old_token_123"
        new_token = "new_token_456"

        # Save initial credentials
        CredentialManager.save_credentials(username, old_token)

        # Update token
        CredentialManager.update_token(new_token)

        # Verify username unchanged, token updated
        loaded = CredentialManager.load_credentials()
        assert loaded == (username, new_token)

    def test_update_token_no_credentials(self, mock_keyring: dict) -> None:
        """Test updating token when no credentials exist."""
        with pytest.raises(ValueError, match="No existing credentials"):
            CredentialManager.update_token("new_token")

    def test_update_username(self, mock_keyring: dict) -> None:
        """Test updating only the username."""
        old_username = "olduser"
        new_username = "newuser"
        token = "token_123"

        # Save initial credentials
        CredentialManager.save_credentials(old_username, token)

        # Update username
        CredentialManager.update_username(new_username)

        # Verify token unchanged, username updated
        loaded = CredentialManager.load_credentials()
        assert loaded == (new_username, token)

    def test_update_username_no_credentials(self, mock_keyring: dict) -> None:
        """Test updating username when no credentials exist."""
        with pytest.raises(ValueError, match="No existing credentials"):
            CredentialManager.update_username("newuser")

    def test_save_overwrites_existing(self, mock_keyring: dict) -> None:
        """Test that saving new credentials overwrites existing ones."""
        # Save first set
        CredentialManager.save_credentials("user1", "token1")

        # Save second set (should overwrite)
        CredentialManager.save_credentials("user2", "token2")

        # Load should return second set
        loaded = CredentialManager.load_credentials()
        assert loaded == ("user2", "token2")

    def test_credential_info_summary(self, mock_keyring: dict) -> None:
        """Test CredentialInfo summary property."""
        username = "testuser"
        token = "1234567890abcdef"

        CredentialManager.save_credentials(username, token)
        info = CredentialManager.get_credential_info()

        assert info is not None
        summary = info.summary
        assert username in summary
        assert str(info.token_length) in summary
        assert "1234" in summary  # First 4 chars
        assert "cdef" in summary  # Last 4 chars
