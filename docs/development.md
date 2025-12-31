# Development Guide

Guide for contributors and developers working on the Discogs Collection Dumper.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Adding Features](#adding-features)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- Basic understanding of async/await in Python
- Familiarity with Click (CLI framework)

### Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/dump-discogs-collection-2-csv.git
cd dump-discogs-collection-2-csv

# Add upstream remote
git remote add upstream https://github.com/blackbunt/dump-discogs-collection-2-csv.git
```

## Development Setup

### Create Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Install Development Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# This installs:
# - The package itself (editable)
# - Production dependencies (aiohttp, click, etc.)
# - Development tools (pytest, mypy, ruff, etc.)
```

### Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# The hooks will run automatically on git commit
# To run manually:
pre-commit run --all-files
```

### Verify Setup

```bash
# Check Python version
python --version

# Check tools are available
ruff --version
mypy --version
pytest --version

# Run tests
pytest

# Check types
mypy src/

# Lint code
ruff check .
```

## Project Structure

```
dump-discogs-collection-2-csv/
├── pyproject.toml                 # Build config, dependencies, tool settings
├── .pre-commit-config.yaml        # Pre-commit hooks config
├── README.md                      # Main documentation
│
├── src/discogs_dumper/            # Source code (src-layout)
│   ├── __init__.py               # Package version
│   ├── __main__.py               # Entry point for python -m
│   │
│   ├── api/                       # Discogs API client
│   │   ├── client.py             # Async API client
│   │   ├── models.py             # Pydantic data models
│   │   ├── rate_limiter.py       # Rate limiting
│   │   ├── paginator.py          # Pagination logic
│   │   └── exceptions.py         # API exceptions
│   │
│   ├── cli/                       # Click CLI
│   │   ├── main.py               # Main CLI group
│   │   ├── utils.py              # CLI utilities
│   │   └── commands/             # Command implementations
│   │       ├── auth.py           # Authentication
│   │       ├── export.py         # Export command
│   │       ├── stats.py          # Statistics
│   │       ├── qr.py             # QR generation
│   │       ├── cover.py          # Cover download
│   │       └── server.py         # Web server
│   │
│   ├── core/                      # Business logic
│   │   ├── collection.py         # Collection fetching
│   │   ├── exporter.py           # Excel/CSV export
│   │   ├── qr_generator.py       # QR code generation
│   │   ├── cover_downloader.py   # Cover art download
│   │   ├── statistics.py         # Statistics
│   │   └── webserver.py          # HTTP server
│   │
│   ├── persistence/               # State & credentials
│   │   ├── credentials.py        # Keyring integration
│   │   ├── state.py              # Progress tracking
│   │   └── models.py             # State models
│   │
│   ├── utils/                     # Utilities
│   │   ├── sanitization.py       # String cleaning
│   │   ├── logging.py            # Loguru setup
│   │   └── paths.py              # Path helpers
│   │
│   └── config/
│       ├── settings.py           # Pydantic settings
│       └── defaults.py           # Constants
│
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   │   ├── test_api_client.py
│   │   ├── test_rate_limiter.py
│   │   ├── test_sanitization.py
│   │   └── ...
│   ├── integration/              # Integration tests
│   │   ├── test_export_workflow.py
│   │   └── ...
│   ├── fixtures/                 # Test data
│   │   └── api_responses.json
│   └── conftest.py               # Pytest configuration
│
├── docs/                          # Documentation
│   ├── installation.md
│   ├── usage.md
│   ├── development.md            # This file
│   └── migration.md
│
└── scripts/                       # Utility scripts
    └── migrate_config.py         # YAML → Keyring migration
```

### Key Architectural Decisions

1. **src-layout**: Package in `src/` directory for proper isolation
2. **Async throughout**: All I/O operations use async/await
3. **Pydantic for validation**: Type-safe data models with validation
4. **Click for CLI**: Modern, composable CLI framework
5. **Keyring for secrets**: OS-native secure credential storage
6. **Rich for UI**: Beautiful progress bars and tables
7. **Type hints everywhere**: Full mypy strict mode compliance

## Code Quality

### Linting and Formatting: ruff

We use [ruff](https://github.com/astral-sh/ruff) for both linting and formatting (replaces black, isort, flake8).

```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Check specific file
ruff check src/discogs_dumper/api/client.py
```

Configuration is in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "N", "S", "B", "A", "C4", "DTZ", "PIE", "PT", "RET", "SIM", "ARG", "PTH", "ERA", "PD", "PL", "NPY", "RUF"]
```

### Type Checking: mypy

We use [mypy](http://mypy-lang.org/) in strict mode.

```bash
# Type check entire project
mypy src/

# Check specific file
mypy src/discogs_dumper/api/client.py

# Show error context
mypy --show-error-context src/
```

Configuration in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-aiofiles]
```

Skip hooks temporarily (not recommended):

```bash
git commit --no-verify -m "WIP: testing"
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=discogs_dumper --cov-report=html

# Run specific test file
pytest tests/unit/test_sanitization.py

# Run specific test
pytest tests/unit/test_sanitization.py::test_sanitize_artist

# Run with verbose output
pytest -v

# Run with DEBUG logging
pytest --log-cli-level=DEBUG

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Writing Tests

#### Unit Tests

Test individual functions/classes in isolation:

```python
# tests/unit/test_sanitization.py
from discogs_dumper.utils.sanitization import sanitize_artist

def test_sanitize_artist():
    """Test artist name sanitization."""
    assert sanitize_artist("Artist (2)") == "Artist"
    assert sanitize_artist("Artist [3]") == "Artist"
    assert sanitize_artist("  Artist  ") == "Artist"
```

#### Async Tests

Use `pytest.mark.asyncio` for async tests:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_fetch_collection():
    """Test collection fetching."""
    mock_client = AsyncMock()
    mock_client.get_collection_all.return_value = [...]

    fetcher = CollectionFetcher(mock_client, "testuser")
    releases = await fetcher.fetch_all()

    assert len(releases) == 10
```

#### Fixtures

Define reusable test data in `conftest.py`:

```python
# tests/conftest.py
import pytest
from discogs_dumper.api.models import Release, BasicInformation

@pytest.fixture
def sample_release():
    """Create a sample release for testing."""
    return Release(
        id=123456,
        instance_id=789012,
        basic_information=BasicInformation(
            id=123456,
            title="Test Album",
            year=2024,
            artists=[...],
            # ...
        ),
    )
```

#### Mock API Responses

Use fixtures for API responses:

```python
# tests/fixtures/api_responses.json
{
  "collection_page": {
    "pagination": {
      "page": 1,
      "pages": 1,
      "per_page": 100,
      "items": 10
    },
    "releases": [...]
  }
}
```

### Coverage Goals

- **Target**: 85%+ overall coverage
- **Critical paths**: 100% coverage for:
  - API client
  - Rate limiter
  - Credential manager
  - State manager

Check coverage:

```bash
# Generate HTML report
pytest --cov=discogs_dumper --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Adding Features

### Creating a New Command

1. **Create command file**:

```python
# src/discogs_dumper/cli/commands/mycommand.py
import click
from discogs_dumper.cli.utils import async_command, info, success

@click.group()
def mycommand() -> None:
    """My new command."""
    pass

@mycommand.command()
@click.option("--option", "-o", help="An option")
@async_command
async def subcommand(option: str | None) -> None:
    """A subcommand."""
    info("Running subcommand...")
    # Your logic here
    success("Done!")
```

2. **Register in main CLI**:

```python
# src/discogs_dumper/cli/main.py
from discogs_dumper.cli.commands.mycommand import mycommand

@click.group()
def cli() -> None:
    """..."""
    pass

cli.add_command(mycommand)
```

3. **Add tests**:

```python
# tests/unit/test_cli_mycommand.py
from click.testing import CliRunner
from discogs_dumper.cli.main import cli

def test_mycommand():
    runner = CliRunner()
    result = runner.invoke(cli, ["mycommand", "subcommand"])
    assert result.exit_code == 0
    assert "Done!" in result.output
```

### Adding a Core Feature

1. **Implement in `core/`**:

```python
# src/discogs_dumper/core/myfeature.py
from loguru import logger

class MyFeature:
    """My new feature."""

    async def process(self) -> None:
        """Process something."""
        logger.debug("Processing...")
        # Your logic here
```

2. **Add Pydantic models if needed**:

```python
# src/discogs_dumper/api/models.py or persistence/models.py
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    """My data model."""

    field1: str = Field(..., description="A required field")
    field2: int = Field(default=0, description="An optional field")
```

3. **Write tests**:

```python
# tests/unit/test_myfeature.py
import pytest
from discogs_dumper.core.myfeature import MyFeature

@pytest.mark.asyncio
async def test_myfeature():
    feature = MyFeature()
    result = await feature.process()
    assert result is not None
```

### Adding API Methods

1. **Add to API client**:

```python
# src/discogs_dumper/api/client.py
async def get_new_endpoint(self) -> MyModel:
    """Fetch from new endpoint."""
    url = f"{self.base_url}/new/endpoint"
    data = await self._request("GET", url)
    return MyModel.model_validate(data)
```

2. **Add Pydantic model**:

```python
# src/discogs_dumper/api/models.py
class MyModel(BaseModel):
    """Response from new endpoint."""
    field1: str
    field2: int
```

3. **Test with mocked responses**:

```python
# tests/unit/test_api_client.py
@pytest.mark.asyncio
async def test_get_new_endpoint(mock_aiohttp_session):
    mock_aiohttp_session.get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value={"field1": "value", "field2": 42}
    )

    async with DiscogsClient("user", "token") as client:
        result = await client.get_new_endpoint()
        assert result.field1 == "value"
        assert result.field2 == 42
```

## Release Process

### Version Bumping

1. **Update version**:

```python
# src/discogs_dumper/__init__.py
__version__ = "2.1.0"
```

2. **Update CHANGELOG** (if exists):

```markdown
## [2.1.0] - 2025-01-15

### Added
- New feature X
- New command Y

### Fixed
- Bug Z
```

3. **Commit**:

```bash
git add src/discogs_dumper/__init__.py CHANGELOG.md
git commit -m "Bump version to 2.1.0"
```

### Creating a Release

1. **Tag the release**:

```bash
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0
```

2. **Build package**:

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Check distribution
twine check dist/*
```

3. **Publish to PyPI**:

```bash
# Test PyPI first (optional)
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

### GitHub Release

1. Go to [Releases](https://github.com/blackbunt/dump-discogs-collection-2-csv/releases)
2. Click "Draft a new release"
3. Select tag `v2.1.0`
4. Add release notes
5. Publish

## Best Practices

### Code Style

1. **Type hints everywhere**:
   ```python
   def process(data: list[Release]) -> pd.DataFrame:
       ...
   ```

2. **Docstrings** (Google style):
   ```python
   def fetch_collection(username: str) -> list[Release]:
       """Fetch collection for a user.

       Args:
           username: Discogs username

       Returns:
           List of releases

       Raises:
           APIError: If API request fails
       """
   ```

3. **Async/await** for I/O:
   ```python
   # Good
   async def fetch_data() -> Data:
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return await response.json()

   # Bad - blocking I/O
   def fetch_data() -> Data:
       response = requests.get(url)
       return response.json()
   ```

4. **Error handling**:
   ```python
   from loguru import logger

   try:
       result = await risky_operation()
   except SpecificError as e:
       logger.error(f"Operation failed: {e}")
       raise  # Re-raise if can't handle
   ```

### Git Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make commits**:
   ```bash
   git add .
   git commit -m "Add my feature"
   ```

3. **Keep up to date**:
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/my-feature
   # Create Pull Request on GitHub
   ```

### Commit Messages

Follow conventional commits:

```
feat: Add new export format
fix: Handle missing cover images
docs: Update installation guide
test: Add tests for rate limiter
refactor: Simplify sanitization logic
chore: Update dependencies
```

## Getting Help

- **Code questions**: Open a [Discussion](https://github.com/blackbunt/dump-discogs-collection-2-csv/discussions)
- **Bugs**: Open an [Issue](https://github.com/blackbunt/dump-discogs-collection-2-csv/issues)
- **Features**: Open an [Issue](https://github.com/blackbunt/dump-discogs-collection-2-csv/issues) with `enhancement` label

## Resources

- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
- [Click Documentation](https://click.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
