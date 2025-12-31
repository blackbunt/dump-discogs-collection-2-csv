# Installation Guide

This guide covers installing the Discogs Collection Dumper on various platforms.

## Requirements

- Python 3.12 or higher
- pip (Python package installer)
- A Discogs account with API token
- Internet connection

## Platform-Specific Prerequisites

### Linux

Python 3.12+ should be available in most modern distributions:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# Fedora
sudo dnf install python3.12

# Arch Linux
sudo pacman -S python
```

For keyring support (secure credential storage), install one of:

```bash
# GNOME Keyring (most common)
sudo apt install gnome-keyring

# KWallet (KDE)
sudo apt install kwalletmanager
```

### macOS

Install Python 3.12+ using Homebrew:

```bash
brew install python@3.12
```

Keyring support is built into macOS (Keychain).

### Windows

Download and install Python 3.12+ from [python.org](https://www.python.org/downloads/):

1. Download the installer
2. **Important**: Check "Add Python to PATH"
3. Run the installer
4. Verify: `python --version`

Keyring support is built into Windows (Credential Manager).

## Installation Methods

### Method 1: From Source (Recommended for Development)

This method is best if you want to contribute or need the latest features:

```bash
# Clone the repository
git clone https://github.com/blackbunt/dump-discogs-collection-2-csv.git
cd dump-discogs-collection-2-csv

# Create virtual environment
python3.12 -m venv .venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install in editable mode
pip install -e .

# Verify installation
discogs-dumper --version
```

**With development dependencies** (for testing, linting):

```bash
pip install -e ".[dev]"
```

### Method 2: From PyPI (Future)

Once published to PyPI, you'll be able to install with:

```bash
# Create virtual environment (recommended)
python3.12 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install from PyPI
pip install discogs-dumper

# Verify installation
discogs-dumper --version
```

### Method 3: Using pipx (Isolated Installation)

pipx installs CLI tools in isolated environments:

```bash
# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install discogs-dumper
pipx install discogs-dumper

# Verify installation
discogs-dumper --version
```

## Verifying Installation

Check that everything is installed correctly:

```bash
# Check Python version
python --version
# Should show: Python 3.12.x or higher

# Check discogs-dumper is available
discogs-dumper --help

# Check keyring support
python -c "import keyring; print(keyring.get_keyring())"
# Should show your platform's keyring backend
```

## Getting Your Discogs API Token

1. Log in to [Discogs](https://www.discogs.com/)
2. Go to [Developer Settings](https://www.discogs.com/settings/developers)
3. Click **Generate new token**
4. Copy the token (you'll need it for authentication)

**Important**: Keep your token secret! Don't share it or commit it to version control.

## First-Time Setup

After installation, authenticate with Discogs:

```bash
# Login (will prompt for username and token)
discogs-dumper auth login

# Verify authentication
discogs-dumper auth status
```

Your credentials are stored securely in your system's keyring:
- **macOS**: Keychain
- **Linux**: Secret Service (GNOME Keyring, KWallet)
- **Windows**: Credential Manager

## Troubleshooting Installation

### Python Version Issues

If `python --version` shows an older version:

```bash
# Try python3
python3 --version

# Or specific version
python3.12 --version

# Use that version to create venv
python3.12 -m venv .venv
```

### Keyring Backend Errors (Linux)

If you see `No recommended backend was available`:

```bash
# Install GNOME Keyring
sudo apt install gnome-keyring

# Or use file-based fallback (less secure)
export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
```

### Permission Errors

If you see permission errors during installation:

```bash
# Use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Or user installation (not recommended)
pip install --user -e .
```

### SSL Certificate Errors

If you encounter SSL errors during API calls:

```bash
# macOS
/Applications/Python\ 3.12/Install\ Certificates.command

# Linux (update ca-certificates)
sudo apt update && sudo apt install ca-certificates
```

### Windows Long Path Issues

If installation fails with path-too-long errors:

1. Enable long paths in Windows:
   - Run `gpedit.msc`
   - Navigate to: Computer Configuration → Administrative Templates → System → Filesystem
   - Enable "Enable Win32 long paths"
2. Or install in a shorter path: `C:\discogs\`

## Updating

### From Source

```bash
cd dump-discogs-collection-2-csv
git pull origin master
pip install -e . --upgrade
```

### From PyPI (Future)

```bash
pip install --upgrade discogs-dumper
```

### Using pipx

```bash
pipx upgrade discogs-dumper
```

## Uninstalling

### Standard Installation

```bash
pip uninstall discogs-dumper
```

### pipx Installation

```bash
pipx uninstall discogs-dumper
```

### Remove Credentials

To also remove stored credentials:

```bash
# Logout first
discogs-dumper auth logout

# Or manually remove from keyring
# macOS: Keychain Access → search "discogs-dumper" → delete
# Linux: seahorse (GNOME) → search "discogs-dumper" → delete
# Windows: Credential Manager → search "discogs-dumper" → remove
```

## Next Steps

- Read the [Usage Guide](usage.md) to learn how to use the tool
- Check the [Development Guide](development.md) if you want to contribute
- See [Migration Guide](migration.md) if upgrading from v1.x
