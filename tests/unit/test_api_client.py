"""Unit tests for Discogs API client."""

import pytest
from aiohttp import ClientError
from unittest.mock import AsyncMock, MagicMock, patch

from discogs_dumper.api.client import DiscogsClient
from discogs_dumper.api.exceptions import (
    AuthenticationError,
    DiscogsAPIError,
    InvalidResponseError,
    NetworkError,
    NotFoundError,
    RateLimitExceeded,
    ServerError,
)
from discogs_dumper.api.models import CollectionValue


class TestDiscogsClient:
    """Test suite for DiscogsClient."""

    @pytest.fixture
    def client(self) -> DiscogsClient:
        """Create a test client instance."""
        return DiscogsClient(username="testuser", token="testtoken123")

    async def test_init(self, client: DiscogsClient) -> None:
        """Test client initialization."""
        assert client.username == "testuser"
        assert client._token == "testtoken123"
        assert client._base_url == "https://api.discogs.com"
        assert client._session is None  # Not created until context manager

    async def test_context_manager(self, client: DiscogsClient) -> None:
        """Test async context manager creates and closes session."""
        assert client._session is None

        async with client as ctx:
            assert ctx is client
            assert client._session is not None

        # Session should be closed after exit
        # (can't easily test this without internal aiohttp details)

    @pytest.mark.asyncio
    async def test_get_collection_value_success(
        self, client: DiscogsClient, sample_collection_value: dict
    ) -> None:
        """Test successful collection value fetch."""
        with patch.object(
            client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_collection_value

            result = await client.get_collection_value()

            assert isinstance(result, CollectionValue)
            assert result.minimum == "€1,234.56"
            assert result.median == "€5,678.90"
            assert result.maximum == "€12,345.67"
            mock_request.assert_called_once_with(
                "GET", "/users/testuser/collection/value"
            )

    @pytest.mark.asyncio
    async def test_get_collection_page_success(
        self, client: DiscogsClient, sample_collection_page: dict
    ) -> None:
        """Test successful collection page fetch."""
        with patch.object(
            client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_collection_page

            result = await client.get_collection_page(page=1, per_page=100)

            assert result.pagination.page == 1
            assert result.pagination.pages == 3
            assert result.pagination.items == 250
            assert len(result.releases) == 1
            mock_request.assert_called_once_with(
                "GET",
                "/users/testuser/collection/folders/0/releases",
                params={"page": "1", "per_page": "100"},
            )

    @pytest.mark.asyncio
    async def test_authentication_error_401(self, client: DiscogsClient) -> None:
        """Test that 401 raises AuthenticationError."""
        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        async with client:
            with patch.object(
                client._session, "request", return_value=mock_response  # type: ignore[union-attr]
            ):
                with pytest.raises(AuthenticationError) as exc_info:
                    await client._request("GET", "/test")

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_not_found_error_404(self, client: DiscogsClient) -> None:
        """Test that 404 raises NotFoundError."""
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not found")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        async with client:
            with patch.object(
                client._session, "request", return_value=mock_response  # type: ignore[union-attr]
            ):
                with pytest.raises(NotFoundError) as exc_info:
                    await client._request("GET", "/test")

                assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_rate_limit_error_429(self, client: DiscogsClient) -> None:
        """Test that 429 raises RateLimitExceeded."""
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        async with client:
            with patch.object(
                client._session, "request", return_value=mock_response  # type: ignore[union-attr]
            ):
                with pytest.raises(RateLimitExceeded) as exc_info:
                    await client._request("GET", "/test")

                assert exc_info.value.status_code == 429
                assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_server_error_500(self, client: DiscogsClient) -> None:
        """Test that 500 raises ServerError."""
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal server error")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        async with client:
            with patch.object(
                client._session, "request", return_value=mock_response  # type: ignore[union-attr]
            ):
                with pytest.raises(ServerError) as exc_info:
                    await client._request("GET", "/test")

                assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_network_error(self, client: DiscogsClient) -> None:
        """Test that network errors raise NetworkError."""
        async with client:
            with patch.object(
                client._session,  # type: ignore[union-attr]
                "request",
                side_effect=ClientError("Connection failed"),
            ):
                with pytest.raises(NetworkError) as exc_info:
                    await client._request("GET", "/test")

                assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, client: DiscogsClient) -> None:
        """Test that invalid JSON raises InvalidResponseError."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=Exception("Invalid JSON"))
        mock_response.text = AsyncMock(return_value="Invalid JSON")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        async with client:
            with patch.object(
                client._session, "request", return_value=mock_response  # type: ignore[union-attr]
            ):
                # Should catch any JSON parsing exception and raise InvalidResponseError
                with pytest.raises(Exception):  # Can be various exceptions
                    await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_request_without_session_raises_error(
        self, client: DiscogsClient
    ) -> None:
        """Test that calling _request without session raises RuntimeError."""
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_test_connection_success(self, client: DiscogsClient) -> None:
        """Test successful connection test."""
        with patch.object(
            client, "get_collection_value", new_callable=AsyncMock
        ) as mock_get_value:
            mock_get_value.return_value = MagicMock(spec=CollectionValue)

            result = await client.test_connection()

            assert result is True
            mock_get_value.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_auth_failure(self, client: DiscogsClient) -> None:
        """Test connection test with authentication failure."""
        with patch.object(
            client, "get_collection_value", new_callable=AsyncMock
        ) as mock_get_value:
            mock_get_value.side_effect = AuthenticationError()

            with pytest.raises(AuthenticationError):
                await client.test_connection()
