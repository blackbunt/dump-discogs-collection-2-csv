# Migration Guide: v1.x → v2.0

This guide helps you migrate from version 1.x to the completely rewritten version 2.0.

## What's New in v2.0

Version 2.0 is a **complete rewrite** with modern Python best practices:

### New Features

- **Secure Credentials**: API tokens stored in OS keyring (Keychain/Secret Service/Credential Manager) instead of plaintext YAML
- **Modern CLI**: Click-based command-line interface with subcommands instead of interactive menu
- **Async/Await**: Significantly faster with concurrent API requests and downloads
- **Progress Persistence**: Pause and resume long exports
- **Better Logging**: Loguru with configurable verbosity
- **Type Safety**: Full type hints with Pydantic v2 validation
- **Better UX**: Rich progress bars and formatted output

### What Changed

| Aspect | v1.x | v2.0 |
|--------|------|------|
| Python Version | 3.8+ | 3.12+ |
| Command | `python main.py` | `discogs-dumper` |
| Interface | Interactive menu | CLI commands |
| Credentials | `config/config.yaml` | OS Keyring |
| Installation | Manual | `pip install -e .` |
| Configuration | YAML file | Environment variables |
| Code Structure | Flat | src-layout |
| Type Checking | None | mypy strict |
| Linting | Multiple tools | ruff (all-in-one) |

### What Stayed the Same

- ✅ Excel/CSV export format is identical
- ✅ QR codes are generated the same way
- ✅ Web server uses same port (1224)
- ✅ Output file structure unchanged
- ✅ Discogs API usage unchanged
- ✅ Cover art download format unchanged

## Breaking Changes

### 1. Command-Line Interface

**Old (v1.x)**: Interactive menu

```bash
python main.py
# Shows interactive menu:
# 1. Export collection
# 2. Statistics
# etc.
```

**New (v2.0)**: CLI commands

```bash
# Install first
pip install -e .

# Then use commands
discogs-dumper export
discogs-dumper stats
discogs-dumper auth login
```

### 2. Authentication

**Old (v1.x)**: `config/config.yaml`

```yaml
# config/config.yaml
User:
  username: myusername
  token: my_api_token_here
```

**New (v2.0)**: OS Keyring

```bash
# Login command (credentials stored securely)
discogs-dumper auth login

# Prompts:
# Username: myusername
# Token: my_api_token_here

# Credentials stored in:
# - macOS: Keychain
# - Linux: GNOME Keyring / KWallet
# - Windows: Credential Manager
```

### 3. Configuration

**Old (v1.x)**: `config/config.yaml`

```yaml
Settings:
  qr_output_folder: qr
  cover_output_folder: Cover-Art
  webserver_port: 1224
```

**New (v2.0)**: Environment variables or `.env` file

```bash
# Environment variables
export DISCOGS_QR_OUTPUT_DIR=qr
export DISCOGS_COVER_OUTPUT_DIR=Cover-Art
export DISCOGS_WEBSERVER_PORT=1224

# Or .env file
echo "DISCOGS_QR_OUTPUT_DIR=qr" >> .env
echo "DISCOGS_COVER_OUTPUT_DIR=Cover-Art" >> .env
```

### 4. Feature Removed: Benchmark

The benchmark feature from v1.x has been removed in v2.0 as it was complex and not widely used.

**Old (v1.x)**:
```python
# Available in menu
# 5. Benchmark
```

**New (v2.0)**:
```bash
# Not available
# If needed for development, write custom benchmark script
```

## Step-by-Step Migration

### Step 1: Backup Your Data

Before migrating, backup your existing data:

```bash
# Backup old config
cp config/config.yaml config/config.yaml.backup

# Backup exports (if any)
cp *.xlsx backups/
cp -r qr/ backups/
cp -r Cover-Art/ backups/
```

### Step 2: Check Python Version

v2.0 requires Python 3.12+:

```bash
# Check version
python --version

# Should be: Python 3.12.x or higher
```

If you have an older version, install Python 3.12+:

```bash
# macOS (Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv

# Fedora
sudo dnf install python3.12

# Windows
# Download from python.org
```

### Step 3: Install v2.0

```bash
# Navigate to project directory
cd dump-discogs-collection-2-csv

# Checkout latest version (if using git)
git fetch
git checkout master  # or specific tag like v2.0.0

# Create new virtual environment
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install package
pip install -e .

# Verify installation
discogs-dumper --version
```

### Step 4: Migrate Credentials

#### Automatic Migration

On first login, v2.0 will detect old credentials:

```bash
discogs-dumper auth login

# If config/config.yaml exists:
# ✓ Found credentials in config/config.yaml
# ? Migrate to secure keyring? [Y/n]: Y
# ✓ Credentials migrated successfully
# ? Delete old config.yaml? [y/N]: y
```

#### Manual Migration

If automatic migration doesn't work:

```bash
# 1. Read old config
cat config/config.yaml

# Note your username and token

# 2. Login manually
discogs-dumper auth login
# Enter username and token when prompted

# 3. Verify
discogs-dumper auth status

# 4. Delete old config (optional)
rm config/config.yaml
```

### Step 5: Update Your Workflow

**Old workflow (v1.x)**:

```bash
python main.py
# Select: 1. Export collection
# Select format: 1. Excel
# Done
```

**New workflow (v2.0)**:

```bash
# One command
discogs-dumper export

# Or with options
discogs-dumper export --format excel --include-qr --include-cover
```

### Step 6: Update Scripts

If you have scripts that call the old version:

**Old script**:

```bash
#!/bin/bash
cd /path/to/project
source venv/bin/activate
python main.py
# Then interact with menu...
```

**New script**:

```bash
#!/bin/bash
cd /path/to/project
source .venv/bin/activate

# Direct export
discogs-dumper export --format excel --output collection-$(date +%Y-%m-%d).xlsx
```

### Step 7: Test Everything

Verify all features work:

```bash
# Check authentication
discogs-dumper auth status

# Test export
discogs-dumper export --format excel

# Test statistics
discogs-dumper stats

# Test QR generation
discogs-dumper qr generate

# Test cover download
discogs-dumper cover download

# Test web server
discogs-dumper server start
# Ctrl+C to stop
```

## Command Mapping

Reference for mapping v1.x menu options to v2.0 commands:

| v1.x Menu Option | v2.0 Command |
|------------------|--------------|
| 1. Export collection (Excel) | `discogs-dumper export --format excel` |
| 2. Export collection (CSV) | `discogs-dumper export --format csv` |
| 3. Generate QR codes | `discogs-dumper qr generate` |
| 4. Download cover art | `discogs-dumper cover download` |
| 5. Start web server | `discogs-dumper server start` |
| 6. Collection statistics | `discogs-dumper stats` |
| 7. Benchmark | *(removed)* |
| 8. Settings | Environment variables / `.env` file |
| 9. Exit | Ctrl+C or just exit shell |

## Configuration Mapping

Reference for mapping v1.x YAML config to v2.0 environment variables:

| v1.x YAML Key | v2.0 Environment Variable |
|---------------|---------------------------|
| `User.username` | Stored in keyring (login with `auth login`) |
| `User.token` | Stored in keyring (login with `auth login`) |
| `Settings.qr_output_folder` | `DISCOGS_QR_OUTPUT_DIR` |
| `Settings.cover_output_folder` | `DISCOGS_COVER_OUTPUT_DIR` |
| `Settings.webserver_port` | `DISCOGS_WEBSERVER_PORT` |
| `API.base_url` | `DISCOGS_API_BASE_URL` |
| `API.rate_limit` | `DISCOGS_API_RATE_LIMIT_CALLS` |
| `API.per_page` | `DISCOGS_API_PER_PAGE` |

## Troubleshooting Migration

### Can't Find `discogs-dumper` Command

**Problem**: `command not found: discogs-dumper`

**Solutions**:

```bash
# 1. Ensure virtual environment is activated
source .venv/bin/activate

# 2. Reinstall package
pip install -e .

# 3. Use full path (if needed)
python -m discogs_dumper --help

# 4. Check Python version
python --version  # Must be 3.12+
```

### Keyring Errors on Linux

**Problem**: `No recommended backend was available`

**Solutions**:

```bash
# Install GNOME Keyring
sudo apt install gnome-keyring

# Or install KWallet (KDE)
sudo apt install kwalletmanager

# Or use file-based fallback (less secure)
export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
```

### Old Config Not Detected

**Problem**: Automatic migration doesn't find old config

**Solution**: Manually enter credentials:

```bash
# 1. Read old config
cat config/config.yaml

# 2. Login with those credentials
discogs-dumper auth login
# Enter username and token manually
```

### Export Format Different

**Problem**: Excel file looks different

**Check**: v2.0 should produce identical Excel format. If different:

```bash
# Compare column names
# v1.x and v2.0 should have identical columns

# If issues, report as bug:
# https://github.com/blackbunt/dump-discogs-collection-2-csv/issues
```

### Missing QR Codes or Covers

**Problem**: Old QR codes/covers not found

**Solution**: Directories unchanged, but check:

```bash
# Default directories are the same
ls qr/
ls Cover-Art/

# If different location, set environment variable
export DISCOGS_QR_OUTPUT_DIR=/path/to/qr
export DISCOGS_COVER_OUTPUT_DIR=/path/to/covers
```

## Rollback to v1.x

If you need to rollback:

```bash
# 1. Checkout old version
git checkout v1.0.0  # or whatever old tag/branch

# 2. Restore old venv (if backed up)
rm -rf .venv
mv .venv.backup .venv
source .venv/bin/activate

# 3. Restore old config
cp config/config.yaml.backup config/config.yaml

# 4. Run old version
python main.py
```

## Getting Help

If you encounter issues during migration:

1. **Check this guide**: Re-read relevant sections
2. **Check logs**: Use `--verbose` flag for detailed output
   ```bash
   discogs-dumper --verbose export
   ```
3. **Check authentication**: Verify credentials
   ```bash
   discogs-dumper auth status
   ```
4. **Open an issue**: [GitHub Issues](https://github.com/blackbunt/dump-discogs-collection-2-csv/issues)
   - Include version: `discogs-dumper --version`
   - Include error messages
   - Include platform: Linux/macOS/Windows

## Benefits of v2.0

Once migrated, you'll benefit from:

- **Security**: No plaintext tokens in config files
- **Speed**: Async operations are much faster
- **Reliability**: Resume interrupted exports
- **Convenience**: Simple CLI commands instead of menu navigation
- **Automation**: Easy to script and schedule
- **Quality**: Better error handling and logging
- **Modern**: Latest Python best practices

## Recommended Post-Migration

After successful migration:

1. **Delete old config** (if not already):
   ```bash
   rm config/config.yaml
   ```

2. **Update documentation**: If you have internal docs, update commands

3. **Update scripts**: Modernize any automation scripts

4. **Set up pre-commit hooks** (for contributors):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Star the repo** on GitHub if you find v2.0 useful!

## Questions?

- Read [Usage Guide](usage.md) for detailed command documentation
- Read [Development Guide](development.md) if contributing
- Open [GitHub Discussion](https://github.com/blackbunt/dump-discogs-collection-2-csv/discussions) for questions
