#!/usr/bin/env python3
"""Migration script for moving credentials from YAML to OS keyring.

This script helps users migrate from the old config.yaml storage
(which stored credentials in plaintext) to the new secure keyring storage.

Usage:
    python scripts/migrate_config.py [--config-path PATH] [--delete-yaml]
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
    from loguru import logger

    # Add src to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from discogs_dumper.persistence.credentials import CredentialManager
except ImportError as e:
    print(f"Error: Missing dependencies. Run 'pip install -e .' first")
    print(f"Details: {e}")
    sys.exit(1)


def load_yaml_credentials(config_path: Path) -> tuple[str, str] | None:
    """Load credentials from old YAML config file.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Tuple of (username, token) if found, None otherwise.
    """
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        username = config.get("Login", {}).get("username")
        token = config.get("Login", {}).get("apitoken")

        if not username or not token:
            logger.error("Config file missing 'Login.username' or 'Login.apitoken'")
            return None

        logger.info(f"Found credentials in YAML for user: {username}")
        return (username, token)

    except Exception as e:
        logger.error(f"Failed to read YAML config: {e}")
        return None


def migrate_credentials(
    config_path: Path,
    delete_yaml: bool = False,
    force: bool = False,
) -> bool:
    """Migrate credentials from YAML to keyring.

    Args:
        config_path: Path to config.yaml file
        delete_yaml: Whether to delete YAML credentials after migration
        force: Overwrite existing keyring credentials without prompting

    Returns:
        True if migration successful, False otherwise.
    """
    logger.info("Starting credential migration...")

    # Check if credentials already exist in keyring
    if CredentialManager.has_credentials() and not force:
        logger.warning("Credentials already exist in keyring!")

        existing = CredentialManager.get_credential_info()
        if existing:
            logger.info(f"Existing credentials: {existing.summary}")

        response = input("Overwrite existing credentials? [y/N]: ")
        if response.lower() != "y":
            logger.info("Migration cancelled")
            return False

    # Load credentials from YAML
    creds = load_yaml_credentials(config_path)
    if not creds:
        return False

    username, token = creds

    # Display what will be migrated
    print("\n" + "=" * 60)
    print("Migration Summary:")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Token:    {token[:4]}...{token[-4:]} ({len(token)} characters)")
    print(f"From:     {config_path}")
    print(f"To:       OS Keyring (secure storage)")
    print("=" * 60 + "\n")

    # Confirm migration
    if not force:
        response = input("Proceed with migration? [Y/n]: ")
        if response.lower() == "n":
            logger.info("Migration cancelled")
            return False

    # Save to keyring
    try:
        CredentialManager.save_credentials(username, token)
        logger.success(f"✓ Credentials migrated successfully for user: {username}")

    except Exception as e:
        logger.error(f"✗ Failed to save credentials to keyring: {e}")
        return False

    # Verify saved credentials
    loaded = CredentialManager.load_credentials()
    if not loaded or loaded != (username, token):
        logger.error("✗ Verification failed! Credentials not saved correctly")
        return False

    logger.success("✓ Credentials verified in keyring")

    # Optionally delete YAML credentials
    if delete_yaml:
        print("\n" + "=" * 60)
        print("WARNING: This will REMOVE credentials from YAML file!")
        print("=" * 60)
        print(f"File: {config_path}")
        print("\nThe YAML file will be updated to remove Login section.")
        print("A backup will be created at: {}.backup".format(config_path))
        print("=" * 60 + "\n")

        if not force:
            response = input("Delete credentials from YAML? [y/N]: ")
            if response.lower() != "y":
                logger.info("YAML file left unchanged")
                return True

        try:
            # Create backup
            backup_path = Path(str(config_path) + ".backup")
            import shutil

            shutil.copy2(config_path, backup_path)
            logger.info(f"Backup created: {backup_path}")

            # Remove Login section from YAML
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if "Login" in config:
                del config["Login"]

                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, default_flow_style=False)

                logger.success(f"✓ Credentials removed from {config_path}")
            else:
                logger.info("No Login section found in YAML (already removed?)")

        except Exception as e:
            logger.error(f"✗ Failed to update YAML file: {e}")
            logger.info("Credentials are safely stored in keyring, YAML unchanged")
            return True

    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print("Your credentials are now stored securely in your OS keyring.")
    print("You can now use 'discogs-dumper' commands without config.yaml")
    print("=" * 60 + "\n")

    return True


def main() -> int:
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Migrate Discogs credentials from YAML to OS keyring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate with default config path
  python scripts/migrate_config.py

  # Migrate specific config file
  python scripts/migrate_config.py --config-path /path/to/config.yaml

  # Migrate and delete YAML credentials
  python scripts/migrate_config.py --delete-yaml

  # Force migration without prompts (use with caution!)
  python scripts/migrate_config.py --force --delete-yaml
        """,
    )

    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("config/config.yaml"),
        help="Path to config.yaml file (default: config/config.yaml)",
    )

    parser.add_argument(
        "--delete-yaml",
        action="store_true",
        help="Delete credentials from YAML after successful migration",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force migration without prompts (use with caution!)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    # Run migration
    success = migrate_credentials(
        config_path=args.config_path,
        delete_yaml=args.delete_yaml,
        force=args.force,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
