"""Application settings using Pydantic.

Provides configuration management with environment variable support,
validation, and sensible defaults.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support.

    All settings can be overridden via environment variables with
    the prefix DISCOGS_ (e.g., DISCOGS_API_BASE_URL).

    Settings can also be loaded from a .env file if present.
    """

    model_config = SettingsConfigDict(
        env_prefix="DISCOGS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars
    )

    # API Configuration
    api_base_url: str = Field(
        default="https://api.discogs.com",
        description="Base URL for Discogs API",
    )

    api_version: str = Field(
        default="v2",
        description="Discogs API version",
    )

    api_rate_limit_calls: int = Field(
        default=60,
        description="Maximum API calls per period (authenticated users)",
        ge=1,
        le=1000,
    )

    api_rate_limit_period: float = Field(
        default=60.0,
        description="Rate limit period in seconds",
        gt=0,
    )

    api_per_page: int = Field(
        default=100,
        description="Number of items per page in API requests",
        ge=1,
        le=100,  # Discogs maximum
    )

    api_timeout: float = Field(
        default=30.0,
        description="API request timeout in seconds",
        gt=0,
    )

    # User Agent
    user_agent: str = Field(
        default="DiscogsCollectionDumper/2.0.0 +https://github.com/blackbunt/dump-discogs-collection-2-csv",
        description="User-Agent header for API requests (required by Discogs)",
    )

    # Output Configuration
    default_export_format: Literal["excel", "csv"] = Field(
        default="excel",
        description="Default export format",
    )

    qr_output_dir: str = Field(
        default="qr",
        description="Directory for QR code images",
    )

    cover_output_dir: str = Field(
        default="Cover-Art",
        description="Directory for cover art images",
    )

    default_output_filename: str = Field(
        default="discogs_collection",
        description="Default filename for exports (without extension)",
    )

    # QR Code Configuration
    qr_code_version: int = Field(
        default=4,
        description="QR code version (size)",
        ge=1,
        le=40,
    )

    qr_code_box_size: int = Field(
        default=5,
        description="Size of each box in the QR code",
        ge=1,
    )

    qr_code_border: int = Field(
        default=0,
        description="Border size around QR code (in boxes)",
        ge=0,
    )

    # Server Configuration
    webserver_port: int = Field(
        default=1224,
        description="Port for local webserver serving QR images",
        ge=1024,
        le=65535,
    )

    webserver_host: str = Field(
        default="localhost",
        description="Host for local webserver",
    )

    # Concurrency Configuration
    max_concurrent_downloads: int = Field(
        default=10,
        description="Maximum number of concurrent downloads (covers/QRs)",
        ge=1,
        le=50,
    )

    max_concurrent_api_pages: int = Field(
        default=5,
        description="Maximum number of concurrent API page fetches",
        ge=1,
        le=20,
    )

    # File Configuration
    excel_engine: Literal["openpyxl", "xlsxwriter"] = Field(
        default="openpyxl",
        description="Engine for Excel file writing",
    )

    csv_delimiter: str = Field(
        default="\t",
        description="Delimiter for CSV files (tab by default)",
    )

    # Progress Configuration
    progress_save_interval: int = Field(
        default=50,
        description="Save progress state every N items",
        ge=1,
    )

    progress_save_interval_seconds: float = Field(
        default=30.0,
        description="Save progress state every N seconds",
        gt=0,
    )

    # Paths
    state_dir: Path = Field(
        default=Path.home() / ".discogs-dumper",
        description="Directory for storing application state",
    )

    # Application Metadata
    app_name: str = Field(
        default="Discogs Collection Dumper",
        description="Application name",
    )

    app_version: str = Field(
        default="2.0.0",
        description="Application version",
    )

    # Development/Debug
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    @property
    def qr_output_path(self) -> Path:
        """Get QR output directory as Path object.

        Returns:
            Path to QR output directory
        """
        return Path(self.qr_output_dir)

    @property
    def cover_output_path(self) -> Path:
        """Get cover art output directory as Path object.

        Returns:
            Path to cover art output directory
        """
        return Path(self.cover_output_dir)

    def ensure_output_directories(self) -> None:
        """Create output directories if they don't exist."""
        self.qr_output_path.mkdir(parents=True, exist_ok=True)
        self.cover_output_path.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
