# Copilot Instructions - Dump Discogs Collection 2 CSV

## Project Overview
This is a Python application that dumps a user's Discogs music collection to Excel or CSV files. It uses the Discogs API to retrieve collection data and can generate QR codes for quick release lookups. A local webserver (port 1224) serves QR images for mail merge operations in Word.

## Tech Stack
- **Language**: Python 3
- **Key Dependencies**:
  - `requests` - API communication with Discogs
  - `pandas` - Data manipulation and Excel/CSV export
  - `qrcode` - QR code image generation
  - `PyYAML` - Configuration file management
  - `pick` - Interactive menu system
  - `tqdm` - Progress bars
  - `ratelimit` - API rate limiting
  - `multiprocessing` - Multithreaded data collection

## Architecture

### Entry Point
- `main.py` / `DumpDiscogs.py` - Main entry point, loads config, checks login, shows menu

### Configuration
- `config/config.yaml` - API settings, credentials (username, API token)
- `config/menu.yaml` - Menu structure configuration

### Core Modules (`module/`)
- `api.py` - Discogs API wrapper functions (headers, queries, URLs, authentication)
- `collection.py` - Main data collection logic with multithreading
- `login.py` - Authentication and connection checking
- `menu.py` - Interactive menu system
- `qr.py` - QR code generation for releases
- `write_to_file.py` - Excel/CSV export functionality
- `cleanup_strings.py` - String cleanup and formatting utilities
- `setup_json.py` - JSON data structure setup
- `config.py` - Config file reading utilities
- `benchmark.py` - Performance benchmarking
- `check_exists.py` - File existence checks
- `gen_url.py` - URL generation helpers
- `url_checker.py` - URL validation

## Code Style Guidelines

### General Principles
- Use UTF-8 encoding (`# -*- coding: utf-8 -*-`)
- Follow PEP 8 style guidelines
- Use type hints where applicable (e.g., `def call_api(url: str):`)
- Keep functions focused and single-purpose
- Use descriptive variable names (e.g., `config_yaml`, `list_manager`)

### API Rate Limiting
- Always use `@sleep_and_retry` and `@limits` decorators for API calls
- Respect Discogs API rate limit: 60 calls per 60 seconds
- Example pattern:
  ```python
  @sleep_and_retry
  @limits(calls=60, period=60)
  def call_api(url: str):
      # implementation
  ```

### Configuration Access
- Load config via `config.read_config(CONFIG_PATH)`
- Store config in YAML format
- Use nested dictionary access for config values
- API credentials: `Login.apitoken` and `Login.username`

### Error Handling
- Check API response status codes (404, 200)
- Exit gracefully with informative messages on critical errors
- Example: `sys.exit('Connection to Discogs not possible.\nNo Network Connection?')`

### Multiprocessing
- Use `multiprocessing.Pool` for parallel API requests
- Implement `Manager()` for shared state across processes
- Use `tqdm` for progress tracking in long operations
- Handle signals properly (SIGINT for graceful shutdown)

### Data Processing
- Use `pandas` for tabular data manipulation
- Clean strings before export (use `cleanup_strings` module)
- Support both Excel and CSV output formats

### File Organization
- Store output files in organized directories
- QR codes in dedicated folder (`qr/`)
- Use absolute paths with `os.path.join()`
- Check file existence before operations

## API Integration

### Discogs API Endpoints
- Collection releases: `/users/{username}/collection/folders/0/releases`
- Collection value: `/users/{username}/collection/value`
- Processing with pagination: `?page={page}&per_page={per_page}&token={token}`

### Headers
- Accept: `application/vnd.discogs.v2.plaintext+json`
- Content-Type: `application/json`
- User-Agent: `Dump Library/1.1 +https://github.com/blackbunt/dump-discogs-collection-2-csv`

### Pagination
- Default per_page: 100 (configurable)
- Use page parameter for iteration
- Handle rate limiting between requests

## Development Guidelines

### When Adding Features
1. Check if functionality exists in existing modules
2. Follow the modular structure (separate concerns)
3. Update config files if adding new settings
4. Add rate limiting for new API calls
5. Include progress indicators for long operations

### When Fixing Bugs
1. Check API rate limiting compliance
2. Verify config file structure matches code expectations
3. Ensure proper error handling for network issues
4. Test with various collection sizes

### Testing Considerations
- Requires valid Discogs API credentials
- Test with small collections first (pagination)
- Verify QR code generation creates valid images
- Check Excel/CSV output formatting
- Test multiprocessing on different CPU counts

## Common Patterns

### Loading Config
```python
CONFIG_PATH = os.path.join(os.getcwd(), 'config/config.yaml')
gen_config = config.read_config(CONFIG_PATH)
```

### API Call with Rate Limiting
```python
@sleep_and_retry
@limits(calls=60, period=60)
def call_api(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        # handle error
    return response
```

### String Cleanup
```python
import module.cleanup_strings as clean
cleaned_artist = clean.cleanup_artist(raw_artist)
cleaned_title = clean.cleanup_title(raw_title)
```

## Important Notes
- **Never commit API tokens** - Config files may contain sensitive credentials
- Local webserver runs on port 1224 - ensure port is available
- Multithreading uses CPU count - be mindful of resource usage
- QR codes link to Discogs release pages for quick mobile lookup
- Designed for Word mail merge integration via local HTTP server
