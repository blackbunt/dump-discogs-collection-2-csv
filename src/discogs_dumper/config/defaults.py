"""Default values and constants for the application.

Defines constants that are used throughout the application and should
not be changed via configuration.
"""

from typing import Final

# Application Information
APP_NAME: Final[str] = "Discogs Collection Dumper"
APP_VERSION: Final[str] = "2.0.0"
APP_AUTHOR: Final[str] = "Bernie"
APP_LICENSE: Final[str] = "MIT"
APP_REPOSITORY: Final[str] = "https://github.com/blackbunt/dump-discogs-collection-2-csv"

# API Constants
API_VERSION: Final[str] = "v2"
API_BASE_URL: Final[str] = "https://api.discogs.com"
HTTPS_BASE_URL: Final[str] = "https://www.discogs.com"

# API Headers
ACCEPT_HEADER: Final[str] = f"application/vnd.discogs.{API_VERSION}.plaintext+json"
CONTENT_TYPE_HEADER: Final[str] = "application/json"

# API Limits (from Discogs documentation)
API_RATE_LIMIT_AUTHENTICATED: Final[int] = 60  # requests per minute
API_RATE_LIMIT_UNAUTHENTICATED: Final[int] = 25  # requests per minute
API_MAX_PER_PAGE: Final[int] = 100  # maximum items per page

# File Extensions
EXCEL_EXTENSION: Final[str] = ".xlsx"
CSV_EXTENSION: Final[str] = ".csv"
QR_EXTENSION: Final[str] = ".png"
COVER_EXTENSION: Final[str] = ".jpg"

# Default Filenames
DEFAULT_OUTPUT_FILENAME: Final[str] = "discogs_collection"
DEFAULT_QR_DIR: Final[str] = "qr"
DEFAULT_COVER_DIR: Final[str] = "Cover-Art"

# QR Code Defaults
QR_CODE_VERSION: Final[int] = 4
QR_CODE_BOX_SIZE: Final[int] = 5
QR_CODE_BORDER: Final[int] = 0
QR_CODE_FILL_COLOR: Final[str] = "black"
QR_CODE_BACK_COLOR: Final[str] = "white"

# Server Defaults
DEFAULT_SERVER_PORT: Final[int] = 1224
DEFAULT_SERVER_HOST: Final[str] = "localhost"

# Timeout Values (in seconds)
DEFAULT_API_TIMEOUT: Final[float] = 30.0
DEFAULT_DOWNLOAD_TIMEOUT: Final[float] = 60.0

# Concurrency Limits
DEFAULT_MAX_CONCURRENT_DOWNLOADS: Final[int] = 10
DEFAULT_MAX_CONCURRENT_API_PAGES: Final[int] = 5

# Progress Saving Intervals
PROGRESS_SAVE_INTERVAL_ITEMS: Final[int] = 50  # Save every N items
PROGRESS_SAVE_INTERVAL_SECONDS: Final[float] = 30.0  # Save every N seconds

# File Size Limits
MAX_FILENAME_LENGTH: Final[int] = 255  # Filesystem limit
MAX_LOG_FILE_SIZE: Final[str] = "10 MB"
LOG_RETENTION_DAYS: Final[str] = "7 days"

# Keyring Constants
KEYRING_SERVICE_NAME: Final[str] = "discogs-dumper"
KEYRING_USERNAME_KEY: Final[str] = "username"
KEYRING_TOKEN_KEY: Final[str] = "token"

# State File Constants
STATE_DIR_NAME: Final[str] = ".discogs-dumper"
STATE_FILE_NAME: Final[str] = "progress.json"
STATE_VERSION: Final[str] = "2.0.0"

# Excel/CSV Column Names
COLUMN_DISCOGS_ID: Final[str] = "discogs_no"
COLUMN_ARTIST: Final[str] = "artist"
COLUMN_ALBUM_TITLE: Final[str] = "album_title"
COLUMN_YEAR: Final[str] = "year"
COLUMN_LABEL: Final[str] = "label"
COLUMN_CATALOG_NUMBER: Final[str] = "catalog_number"
COLUMN_FORMAT: Final[str] = "format"
COLUMN_GENRES: Final[str] = "genres"
COLUMN_STYLES: Final[str] = "styles"
COLUMN_DATE_ADDED: Final[str] = "date_added"
COLUMN_RATING: Final[str] = "rating"
COLUMN_DISCOGS_URL: Final[str] = "discogs_url"
COLUMN_COVER_URL: Final[str] = "cover_url"
COLUMN_QR_URL: Final[str] = "qr_url"

# Export Column Order
EXPORT_COLUMNS: Final[tuple[str, ...]] = (
    COLUMN_DISCOGS_ID,
    COLUMN_ARTIST,
    COLUMN_ALBUM_TITLE,
    COLUMN_YEAR,
    COLUMN_LABEL,
    COLUMN_CATALOG_NUMBER,
    COLUMN_FORMAT,
    COLUMN_GENRES,
    COLUMN_STYLES,
    COLUMN_DATE_ADDED,
    COLUMN_RATING,
    COLUMN_DISCOGS_URL,
    COLUMN_COVER_URL,
)

# HTTP Status Codes (for clarity)
HTTP_OK: Final[int] = 200
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_UNAUTHORIZED: Final[int] = 401
HTTP_FORBIDDEN: Final[int] = 403
HTTP_NOT_FOUND: Final[int] = 404
HTTP_RATE_LIMIT: Final[int] = 429
HTTP_INTERNAL_ERROR: Final[int] = 500

# Regex Patterns
PATTERN_DISCOGS_NUMBER: Final[str] = r"\(\d+\)$"  # Matches (2), (123), etc.
PATTERN_SLASH_SPACE_SLASH: Final[str] = r" / "
PATTERN_TRAILING_HYPHEN: Final[str] = r"-+$"
PATTERN_NON_WORD_CHARS: Final[str] = r"\W+"

# Display Formatting
PROGRESS_BAR_WIDTH: Final[int] = 50
TABLE_MAX_WIDTH: Final[int] = 120
