"""QR code generation for Discogs releases.

Generates QR codes containing Discogs URLs for easy mobile access
to release information.
"""

import asyncio
from pathlib import Path
from typing import Any

import qrcode
from loguru import logger

from discogs_dumper.api.models import Release
from discogs_dumper.config.settings import settings
from discogs_dumper.utils.sanitization import create_safe_filename


class QRGenerator:
    """Generates QR codes for Discogs releases.

    Creates QR code images containing URLs to Discogs release pages,
    useful for quickly accessing release information on mobile devices.

    Attributes:
        output_dir: Directory where QR codes will be saved
        version: QR code version (size), 1-40 (default: 4)
        box_size: Size of each box in pixels (default: 5)
        border: Border size in boxes (default: 0)

    Examples:
        >>> generator = QRGenerator()
        >>> await generator.generate_for_releases(releases)
        >>> print(f"QR codes saved to {generator.output_dir}")
    """

    def __init__(
        self,
        output_dir: Path | str | None = None,
        *,
        version: int | None = None,
        box_size: int | None = None,
        border: int | None = None,
    ) -> None:
        """Initialize QR code generator.

        Args:
            output_dir: Output directory for QR codes (default: from settings)
            version: QR code version 1-40 (default: from settings)
            box_size: Size of each box in pixels (default: from settings)
            border: Border size in boxes (default: from settings)
        """
        self.output_dir = Path(output_dir) if output_dir else settings.qr_output_path
        self.version = version if version is not None else settings.qr_code_version
        self.box_size = box_size if box_size is not None else settings.qr_code_box_size
        self.border = border if border is not None else settings.qr_code_border

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_qr_code(self, url: str) -> qrcode.QRCode:
        """Create QR code object for URL.

        Args:
            url: URL to encode in QR code

        Returns:
            Configured QR code object
        """
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(url)
        qr.make(fit=True)
        return qr

    def _generate_qr_sync(
        self,
        release: Release,
        *,
        skip_existing: bool = True,
    ) -> Path | None:
        """Generate QR code for a single release (synchronous).

        Args:
            release: Release to generate QR code for
            skip_existing: Skip if QR code already exists (default: True)

        Returns:
            Path to generated QR code, or None if skipped
        """
        # Create safe filename
        artist = release.basic_information.artists[0].name
        title = release.basic_information.title
        filename = create_safe_filename(
            artist=artist,
            title=title,
            discogs_id=release.id,
            extension="png",
        )

        output_path = self.output_dir / filename

        # Skip if exists
        if skip_existing and output_path.exists():
            logger.debug(f"QR code already exists, skipping: {filename}")
            return None

        # Generate QR code
        url = release.discogs_webpage
        qr = self._create_qr_code(url)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save
        img.save(str(output_path))
        logger.debug(f"Generated QR code: {filename}")

        return output_path

    async def generate_for_release(
        self,
        release: Release,
        *,
        skip_existing: bool = True,
    ) -> Path | None:
        """Generate QR code for a single release (async).

        Args:
            release: Release to generate QR code for
            skip_existing: Skip if QR code already exists (default: True)

        Returns:
            Path to generated QR code, or None if skipped

        Examples:
            >>> path = await generator.generate_for_release(release)
            >>> if path:
            ...     print(f"QR code saved to {path}")
        """
        # Run CPU-bound QR generation in thread pool
        return await asyncio.to_thread(
            self._generate_qr_sync,
            release,
            skip_existing=skip_existing,
        )

    async def generate_for_releases(
        self,
        releases: list[Release],
        *,
        skip_existing: bool = True,
        max_concurrent: int = 10,
        progress_callback: Any = None,
    ) -> list[Path]:
        """Generate QR codes for multiple releases.

        Args:
            releases: List of releases to generate QR codes for
            skip_existing: Skip existing QR codes (default: True)
            max_concurrent: Max concurrent generations (default: 10)
            progress_callback: Optional callback with (current, total)

        Returns:
            List of paths to generated QR codes (excludes skipped)

        Examples:
            >>> async def progress(current, total):
            ...     print(f"Generated {current}/{total}")
            >>> paths = await generator.generate_for_releases(
            ...     releases,
            ...     progress_callback=progress
            ... )
        """
        logger.info(f"Generating QR codes for {len(releases)} releases")

        semaphore = asyncio.Semaphore(max_concurrent)
        generated_paths: list[Path] = []

        async def generate_with_semaphore(
            release: Release,
            index: int,
        ) -> Path | None:
            """Generate QR with semaphore control."""
            async with semaphore:
                path = await self.generate_for_release(
                    release,
                    skip_existing=skip_existing,
                )

                # Progress callback
                if progress_callback:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(index + 1, len(releases))
                    else:
                        progress_callback(index + 1, len(releases))

                return path

        # Generate all QR codes concurrently
        tasks = [
            generate_with_semaphore(release, i) for i, release in enumerate(releases)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None and exceptions
        for result in results:
            if isinstance(result, Path):
                generated_paths.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error generating QR code: {result}")

        logger.info(
            f"Generated {len(generated_paths)} QR codes "
            f"(skipped {len(releases) - len(generated_paths)})"
        )

        return generated_paths

    def get_qr_path_for_release(self, release: Release) -> Path:
        """Get the expected QR code path for a release.

        Args:
            release: Release to get QR path for

        Returns:
            Expected path to QR code file

        Examples:
            >>> path = generator.get_qr_path_for_release(release)
            >>> if path.exists():
            ...     print("QR code exists")
        """
        artist = release.basic_information.artists[0].name
        title = release.basic_information.title
        filename = create_safe_filename(
            artist=artist,
            title=title,
            discogs_id=release.id,
            extension="png",
        )
        return self.output_dir / filename

    def clear_all(self) -> int:
        """Delete all QR codes in output directory.

        Returns:
            Number of QR codes deleted

        Examples:
            >>> deleted = generator.clear_all()
            >>> print(f"Deleted {deleted} QR codes")
        """
        if not self.output_dir.exists():
            return 0

        count = 0
        for qr_file in self.output_dir.glob("*.png"):
            qr_file.unlink()
            count += 1

        logger.info(f"Deleted {count} QR codes from {self.output_dir}")
        return count


async def generate_qr_codes(
    releases: list[Release],
    output_dir: Path | str | None = None,
    *,
    skip_existing: bool = True,
    progress_callback: Any = None,
) -> list[Path]:
    """Convenience function to generate QR codes for releases.

    Args:
        releases: List of releases to generate QR codes for
        output_dir: Output directory (default: from settings)
        skip_existing: Skip existing QR codes (default: True)
        progress_callback: Optional progress callback

    Returns:
        List of paths to generated QR codes

    Examples:
        >>> paths = await generate_qr_codes(releases)
        >>> print(f"Generated {len(paths)} QR codes")
    """
    generator = QRGenerator(output_dir=output_dir)
    return await generator.generate_for_releases(
        releases,
        skip_existing=skip_existing,
        progress_callback=progress_callback,
    )
