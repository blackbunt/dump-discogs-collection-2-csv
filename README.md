# Discogs Collection Dumper

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

A modern Python tool for exporting your Discogs vinyl collection to Excel or CSV, with support for QR codes, cover art, and collection statistics.

## ✨ Features

- 🎵 **Export Collection** - Export to Excel (.xlsx) or CSV formats
- 📊 **Collection Statistics** - View value, top artists, labels, and more
- 📷 **QR Code Generation** - Create QR codes for quick mobile access to releases
- 🖼️ **Cover Art Download** - Download cover images for your collection
- 🌐 **Web Server** - Serve QR codes via HTTP for embedding in Excel
- 💾 **Resume Support** - Pause and resume long exports
- 🔒 **Secure Credentials** - API tokens stored in OS keyring (not plaintext!)
- ⚡ **Async/Await** - Fast concurrent API requests and downloads
- 🎨 **Rich CLI** - Beautiful progress bars and formatted output
- 🧪 **Type-Safe** - Full type hints with Pydantic v2 validation

## 📋 Requirements

- Python 3.12 or higher
- Discogs account with API token
- Internet connection

## 🚀 Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/blackbunt/dump-discogs-collection-2-csv.git
cd dump-discogs-collection-2-csv

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Using pip (Future)

```bash
pip install discogs-dumper
```

## 🔑 Getting Your API Token

1. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
2. Click **Generate new token**
3. Copy the token (you'll need it for authentication)

## 📖 Usage

### First Time Setup

```bash
# Login with your Discogs credentials
discogs-dumper auth login

# Check authentication status
discogs-dumper auth status
```

Your credentials are stored securely in your system's keyring:
- **macOS**: Keychain
- **Linux**: Secret Service (GNOME Keyring, KWallet)
- **Windows**: Credential Manager

### Export Your Collection

```bash
# Basic export to Excel
discogs-dumper export

# Export to CSV
discogs-dumper export --format csv --output my_collection.csv

# Export with QR codes and cover art
discogs-dumper export --include-qr --include-cover

# Resume an interrupted export
discogs-dumper export --resume
```

### View Statistics

```bash
# Show collection value and summary
discogs-dumper stats

# Show top 10 artists
discogs-dumper stats --top-artists

# Show top 5 labels
discogs-dumper stats --top-labels --top-n 5

# Show everything
discogs-dumper stats --top-artists --top-labels
```

### Generate QR Codes

```bash
# Generate QR codes for all releases
discogs-dumper qr generate

# Generate to custom directory
discogs-dumper qr generate --output-dir my-qr-codes/

# Overwrite existing QR codes
discogs-dumper qr generate --overwrite
```

### Download Cover Art

```bash
# Download cover art for all releases
discogs-dumper cover download

# Download to custom directory
discogs-dumper cover download --output-dir my-covers/

# Overwrite existing covers
discogs-dumper cover download --overwrite
```

### Web Server for QR Codes

```bash
# Start server on default port (1224)
discogs-dumper server start

# Start on custom port
discogs-dumper server start --port 8080

# Serve from custom directory
discogs-dumper server start --directory custom-qr/
```

The web server allows you to embed QR codes in Excel files using URLs like:
```
http://localhost:1224/123456_Artist_Name-Album_Title.png
```

### Global Options

```bash
# Verbose output (show DEBUG/INFO logs)
discogs-dumper --verbose export

# Quiet mode (only errors)
discogs-dumper --quiet export

# Write logs to file
discogs-dumper --log-file debug.log export
```

## 📂 Output Structure

```
.
├── discogs_collection.xlsx   # Export file
├── qr/                        # QR codes (if generated)
│   ├── 123456_Artist-Album.png
│   └── ...
├── Cover-Art/                 # Cover images (if downloaded)
│   ├── 123456_Artist-Album.jpg
│   └── ...
└── .discogs-dumper/           # Application state
    └── progress.json          # Resume progress
```

## 🔧 Configuration

The tool uses sensible defaults, but you can customize via environment variables:

```bash
# API settings
export DISCOGS_API_BASE_URL=https://api.discogs.com
export DISCOGS_API_RATE_LIMIT_CALLS=60
export DISCOGS_API_PER_PAGE=100

# Output settings
export DISCOGS_QR_OUTPUT_DIR=qr
export DISCOGS_COVER_OUTPUT_DIR=Cover-Art
export DISCOGS_DEFAULT_EXPORT_FORMAT=excel

# Server settings
export DISCOGS_WEBSERVER_PORT=1224
export DISCOGS_WEBSERVER_HOST=localhost

# Concurrency
export DISCOGS_MAX_CONCURRENT_DOWNLOADS=10
export DISCOGS_MAX_CONCURRENT_API_PAGES=5
```

Or create a `.env` file in your project directory.

## 🏗️ Architecture

The project follows modern Python best practices:

- **src-layout** structure for proper packaging
- **Async/await** throughout for performance
- **Pydantic v2** for data validation
- **Click** for CLI framework
- **aiohttp** for async HTTP requests
- **Rich** for beautiful terminal output
- **pytest** with async support
- **ruff** for linting and formatting
- **mypy** for static type checking
- **pre-commit** hooks for code quality

### Project Structure

```
src/discogs_dumper/
├── api/              # Discogs API client (async)
│   ├── client.py     # Main API client
│   ├── models.py     # Pydantic data models
│   ├── rate_limiter.py
│   └── exceptions.py
├── cli/              # Click CLI commands
│   ├── main.py       # CLI entry point
│   └── commands/     # Individual commands
├── core/             # Business logic
│   ├── collection.py    # Collection fetching
│   ├── exporter.py      # Excel/CSV export
│   ├── qr_generator.py  # QR code generation
│   ├── cover_downloader.py
│   ├── statistics.py
│   └── webserver.py
├── persistence/      # State & credentials
│   ├── credentials.py   # Keyring integration
│   ├── state.py         # Progress tracking
│   └── models.py
├── utils/            # Utilities
│   ├── sanitization.py
│   └── logging.py
└── config/           # Configuration
    ├── settings.py      # Pydantic settings
    └── defaults.py      # Constants
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=discogs_dumper --cov-report=html

# Run specific test file
pytest tests/unit/test_sanitization.py -v

# Run with verbose logging
pytest --log-cli-level=DEBUG
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src/

# Run all checks (via pre-commit)
pre-commit run --all-files
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

## 🐛 Troubleshooting

### Authentication Issues

```bash
# Remove stored credentials
discogs-dumper auth logout

# Login again
discogs-dumper auth login
```

### Rate Limiting

The Discogs API allows 60 requests/minute for authenticated users. The tool automatically handles rate limiting, but very large collections may take time to export.

### Resume Interrupted Exports

If an export is interrupted:

```bash
# Resume from where it left off
discogs-dumper export --resume
```

Progress is saved every 50 items or 30 seconds.

## 📝 Migration from v1.x

**Version 2.0 is a complete rewrite** with breaking changes:

### What Changed

1. **CLI Interface**: Interactive menu → Click commands
2. **Credentials**: `config.yaml` → OS Keyring (secure!)
3. **Command**: `python main.py` → `discogs-dumper`
4. **Python Version**: 3.8+ → 3.12+

### Migration Steps

1. Install v2.0:
   ```bash
   pip install -e .
   ```

2. Re-authenticate (credentials will be migrated):
   ```bash
   discogs-dumper auth login
   ```

3. Your old `config/config.yaml` can be safely deleted after migration.

### What Stayed the Same

- ✅ Export format (Excel/CSV) is identical
- ✅ QR codes are generated the same way
- ✅ Web server uses the same port (1224)
- ✅ Output files have the same structure

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Make sure to:
- Run tests (`pytest`)
- Format code (`ruff format`)
- Type check (`mypy src/`)
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Discogs](https://www.discogs.com/) for the excellent API
- [Click](https://click.palletsprojects.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Pydantic](https://docs.pydantic.dev/) for data validation

## 📧 Contact

- GitHub: [@blackbunt](https://github.com/blackbunt)
- Repository: [dump-discogs-collection-2-csv](https://github.com/blackbunt/dump-discogs-collection-2-csv)

---

**Made with ❤️ by Bernie**
