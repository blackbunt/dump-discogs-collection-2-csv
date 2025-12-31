# Usage Guide

Complete guide to using the Discogs Collection Dumper CLI.

## Table of Contents

- [Authentication](#authentication)
- [Exporting Your Collection](#exporting-your-collection)
- [Collection Statistics](#collection-statistics)
- [QR Code Generation](#qr-code-generation)
- [Cover Art Download](#cover-art-download)
- [Web Server](#web-server)
- [Global Options](#global-options)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)

## Authentication

All operations require authentication with your Discogs account.

### Login

```bash
discogs-dumper auth login
```

You'll be prompted for:
- **Username**: Your Discogs username
- **API Token**: Your Discogs API token (get it from [Developer Settings](https://www.discogs.com/settings/developers))

Credentials are stored securely in your system's keyring (Keychain on macOS, Secret Service on Linux, Credential Manager on Windows).

### Check Authentication Status

```bash
discogs-dumper auth status
```

Shows:
- Current authenticated username
- Token status (present/missing)
- Keyring backend in use

### Logout

```bash
discogs-dumper auth logout
```

Removes stored credentials from the keyring.

## Exporting Your Collection

The main feature: export your Discogs collection to Excel or CSV.

### Basic Export

```bash
# Export to Excel (default)
discogs-dumper export

# Output: discogs_collection.xlsx
```

### Export to CSV

```bash
discogs-dumper export --format csv

# Custom filename
discogs-dumper export --format csv --output my_vinyl.csv
```

### Export with QR Codes

QR codes link to the Discogs release page for quick mobile access:

```bash
# Generate and include QR codes in export
discogs-dumper export --include-qr

# QR codes saved to: qr/
# Excel includes QR URL column
```

### Export with Cover Art

Download cover images and include URLs in export:

```bash
# Download and include cover art
discogs-dumper export --include-cover

# Cover images saved to: Cover-Art/
# Excel includes cover URL column
```

### Complete Export

```bash
# Everything: QR codes + cover art
discogs-dumper export --include-qr --include-cover --format excel

# Short form
discogs-dumper export -q -c -f excel
```

### Resume Interrupted Export

If an export is interrupted (network issues, Ctrl+C), you can resume:

```bash
discogs-dumper export --resume
```

Progress is automatically saved every 50 items or 30 seconds to `~/.discogs-dumper/progress.json`.

### Export Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--format` | `-f` | Output format (excel/csv) | excel |
| `--output` | `-o` | Output file path | discogs_collection.xlsx |
| `--include-qr` | `-q` | Generate QR codes | False |
| `--include-cover` | `-c` | Download cover art | False |
| `--resume` | `-r` | Resume interrupted export | False |

### Output Columns

The export includes these columns:

| Column | Description |
|--------|-------------|
| discogs_no | Discogs release ID |
| artist | Artist name(s) |
| album_title | Album/release title |
| year | Release year |
| label | Record label |
| catalog_number | Catalog number |
| format | Format (Vinyl, CD, etc.) |
| genres | Genres (comma-separated) |
| styles | Styles (comma-separated) |
| date_added | Date added to collection |
| rating | Your rating (0-5) |
| notes | Your notes |
| qr_url | QR code URL (if --include-qr) |
| cover_url | Cover image URL (if --include-cover) |

## Collection Statistics

View statistics about your collection.

### Basic Stats

```bash
discogs-dumper stats
```

Shows:
- **Minimum Value**: Lowest estimated value
- **Median Value**: Median estimated value
- **Maximum Value**: Highest estimated value

Values are estimated by Discogs based on marketplace data and are shown in your Discogs currency setting.

### Example Output

```
Collection Statistics
━━━━━━━━━━━━━━━━━━━━━━━━
Minimum Value  €1,234.56
Median Value   €2,345.67
Maximum Value  €3,456.78
```

**Note**: The Discogs API doesn't provide item count in the value endpoint. Use `discogs-dumper export --format excel` to see your full collection.

## QR Code Generation

Generate QR codes for all releases in your collection.

### Generate QR Codes

```bash
# Generate to default directory (qr/)
discogs-dumper qr generate

# Custom directory
discogs-dumper qr generate --output-dir my-qr-codes/

# Overwrite existing QR codes
discogs-dumper qr generate --overwrite
```

### QR Code Details

- **Format**: PNG images
- **Content**: Discogs release URL (e.g., `https://www.discogs.com/release/123456`)
- **Filename**: `{release_id}_{artist}-{title}.png`
- **Default behavior**: Skip existing files
- **Use case**: Print and attach to vinyl sleeves for quick mobile lookup

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output-dir` | `-o` | Output directory | qr/ |
| `--skip-existing` | | Skip existing files | True |
| `--overwrite` | | Overwrite existing files | False |

## Cover Art Download

Download cover art images for your collection.

### Download Covers

```bash
# Download to default directory (Cover-Art/)
discogs-dumper cover download

# Custom directory
discogs-dumper cover download --output-dir my-covers/

# Overwrite existing covers
discogs-dumper cover download --overwrite
```

### Cover Art Details

- **Format**: JPG images (as provided by Discogs)
- **Filename**: `{release_id}_{artist}-{title}.jpg`
- **Default behavior**: Skip existing files
- **Note**: Some releases may not have cover art

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output-dir` | `-o` | Output directory | Cover-Art/ |
| `--skip-existing` | | Skip existing files | True |
| `--overwrite` | | Overwrite existing files | False |

## Web Server

Serve QR codes via HTTP for embedding in Excel files.

### Start Server

```bash
# Start on default port (1224)
discogs-dumper server start

# Custom port
discogs-dumper server start --port 8080

# Custom directory
discogs-dumper server start --directory custom-qr/
```

Server runs until stopped with Ctrl+C.

### Accessing QR Codes

Once running, QR codes are accessible at:

```
http://localhost:1224/{release_id}_{artist}-{title}.png
```

### Excel Integration

When exporting with `--include-qr`, the Excel file includes a `qr_url` column with URLs like:

```
http://localhost:1224/123456_Artist_Name-Album_Title.png
```

Excel can display these as images using the `=IMAGE()` function:

1. Open Excel
2. Start the web server: `discogs-dumper server start`
3. Add a new column for QR images
4. Use formula: `=IMAGE(D2)` (where D2 is the qr_url cell)

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--port` | `-p` | Server port | 1224 |
| `--directory` | `-d` | QR code directory | qr/ |

## Global Options

These options work with all commands.

### Verbose Output

Show detailed DEBUG and INFO logs:

```bash
discogs-dumper --verbose export
discogs-dumper -v stats
```

### Quiet Mode

Show only errors (suppress warnings):

```bash
discogs-dumper --quiet export
discogs-dumper -q stats
```

### Log to File

Write logs to a file:

```bash
discogs-dumper --log-file debug.log export

# Combine with verbose
discogs-dumper --verbose --log-file export.log export
```

### Help

```bash
# General help
discogs-dumper --help

# Command-specific help
discogs-dumper export --help
discogs-dumper auth --help
```

### Version

```bash
discogs-dumper --version
```

## Configuration

### Environment Variables

Customize behavior via environment variables:

```bash
# API settings
export DISCOGS_API_BASE_URL=https://api.discogs.com
export DISCOGS_API_RATE_LIMIT_CALLS=60
export DISCOGS_API_RATE_LIMIT_PERIOD=60
export DISCOGS_API_PER_PAGE=100

# Output directories
export DISCOGS_QR_OUTPUT_DIR=qr
export DISCOGS_COVER_OUTPUT_DIR=Cover-Art
export DISCOGS_DEFAULT_EXPORT_FORMAT=excel

# Web server
export DISCOGS_WEBSERVER_PORT=1224
export DISCOGS_WEBSERVER_HOST=localhost

# Concurrency (advanced)
export DISCOGS_MAX_CONCURRENT_DOWNLOADS=10
export DISCOGS_MAX_CONCURRENT_API_PAGES=5
```

### .env File

Create a `.env` file in your project directory:

```bash
# .env
DISCOGS_QR_OUTPUT_DIR=my-qr-codes
DISCOGS_COVER_OUTPUT_DIR=my-covers
DISCOGS_DEFAULT_EXPORT_FORMAT=csv
DISCOGS_WEBSERVER_PORT=8080
```

The tool will automatically load these settings.

## Advanced Usage

### Large Collections

For collections with 1000+ items:

```bash
# Use verbose mode to see progress
discogs-dumper --verbose export

# If interrupted, resume
discogs-dumper export --resume

# Monitor rate limiting
# The tool automatically handles Discogs' 60 requests/minute limit
```

### Automated Exports

Create a scheduled export:

```bash
#!/bin/bash
# export-collection.sh

cd /path/to/discogs-dumper
source .venv/bin/activate

# Export with timestamp
DATE=$(date +%Y-%m-%d)
discogs-dumper export --output "collection-${DATE}.xlsx"
```

Schedule with cron:

```bash
# Daily export at 2 AM
0 2 * * * /path/to/export-collection.sh
```

### Custom Scripts

Use the Python API directly:

```python
import asyncio
from discogs_dumper.api.client import DiscogsClient
from discogs_dumper.core.exporter import CollectionExporter

async def export_my_collection():
    async with DiscogsClient(username="myuser", token="mytoken") as client:
        # Fetch collection
        releases = []
        async for release in client.get_collection_all():
            releases.append(release)

        # Export
        exporter = CollectionExporter()
        df = exporter.to_dataframe(releases)
        exporter.to_excel(df, "my_collection.xlsx")

asyncio.run(export_my_collection())
```

### Processing Specific Releases

Filter releases before export:

```python
from discogs_dumper.core.collection import CollectionFetcher
from discogs_dumper.core.exporter import CollectionExporter

# Fetch all releases
fetcher = CollectionFetcher(client, "myuser")
releases = await fetcher.fetch_all()

# Filter: only vinyl from 2020+
vinyl_releases = [
    r for r in releases
    if r.basic_information.year >= 2020
    and any("Vinyl" in f.name for f in r.basic_information.formats)
]

# Export filtered collection
exporter = CollectionExporter()
df = exporter.to_dataframe(vinyl_releases)
exporter.to_excel(df, "vinyl_2020plus.xlsx")
```

## Troubleshooting

### Rate Limiting

If you see delays, it's normal:

```
⚠ Rate limit approaching, waiting...
```

The Discogs API allows 60 requests/minute. The tool automatically handles this.

### Authentication Errors

```bash
# Re-login
discogs-dumper auth logout
discogs-dumper auth login
```

### Resume Not Working

If resume fails:

```bash
# Clear state and start fresh
rm ~/.discogs-dumper/progress.json
discogs-dumper export
```

### QR Codes Not Generating

Check output directory permissions:

```bash
# Linux/macOS
chmod 755 qr/

# Manually test
discogs-dumper qr generate --verbose
```

### Excel Can't Display Images

1. Ensure web server is running: `discogs-dumper server start`
2. Check firewall isn't blocking port 1224
3. Try custom port: `discogs-dumper server start --port 8080`

## Best Practices

1. **Use virtual environment**: Isolate dependencies
2. **Keep credentials secure**: Never commit tokens to Git
3. **Resume long exports**: Use `--resume` for large collections
4. **Backup exports**: Keep regular backups of your collection data
5. **Monitor rate limits**: Don't run multiple exports simultaneously
6. **Update regularly**: `pip install --upgrade discogs-dumper`

## Getting Help

- **Documentation**: Check [README.md](../README.md)
- **Issues**: Report bugs at [GitHub Issues](https://github.com/blackbunt/dump-discogs-collection-2-csv/issues)
- **CLI Help**: `discogs-dumper --help`
- **Command Help**: `discogs-dumper <command> --help`
