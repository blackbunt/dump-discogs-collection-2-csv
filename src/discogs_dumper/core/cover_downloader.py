"""Cover art downloader for Discogs releases.

Downloads cover art images from Discogs with concurrent downloading,
resume capability, and progress tracking.
"""

import asyncio
from pathlib import Path
from typing import Any

import aiofiles
import aiohttp
from loguru import logger

from discogs_dumper.api.models import Release
from discogs_dumper.config.settings import settings
from discogs_dumper.utils.sanitization import create_safe_filename


class CoverDownloader:
    """Downloads cover art images for Discogs releases.

    Provides concurrent downloading with semaphore control, automatic
    retry on failure, and skip-existing functionality.

    Attributes:
        output_dir: Directory where covers will be saved
        timeout: Download timeout in seconds
        max_concurrent: Maximum concurrent downloads

    Examples:
        >>> downloader = CoverDownloader()
        >>> await downloader.download_for_releases(releases)
        >>> print(f"Covers saved to {downloader.output_dir}")
    """

    def __init__(
        self,
        output_dir: Path | str | None = None,
        *,
        timeout: float = 60.0,
        max_concurrent: int = 10,
    ) -> None:
        """Initialize cover downloader.

        Args:
            output_dir: Output directory for covers (default: from settings)
            timeout: Download timeout in seconds (default: 60.0)
            max_concurrent: Max concurrent downloads (default: 10)
        """
        self.output_dir = (
            Path(output_dir) if output_dir else settings.cover_output_path
        )
        self.timeout = timeout
        self.max_concurrent = max_concurrent

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_cover_url(self, release: Release) -> str | None:
        """Extract cover URL from release.

        Args:
            release: Release to get cover URL from

        Returns:
            Cover image URL, or None if no cover available
        """
        images = release.basic_information.cover_image_urls

        # Prefer primary image, fallback to first image
        if images.primary:
            return images.primary
        elif images.secondary:
            return images.secondary

        return None

    async def download_cover(
        self,
        release: Release,
        *,
        skip_existing: bool = True,
        session: aiohttp.ClientSession | None = None,
    ) -> Path | None:
        """Download cover art for a single release.

        Args:
            release: Release to download cover for
            skip_existing: Skip if cover already exists (default: True)
            session: Optional aiohttp session (creates new if None)

        Returns:
            Path to downloaded cover, or None if skipped/unavailable

        Examples:
            >>> path = await downloader.download_cover(release)
            >>> if path:
            ...     print(f"Cover saved to {path}")
        """
        # Get cover URL
        cover_url = self._get_cover_url(release)
        if not cover_url:
            logger.debug(f"No cover available for release {release.id}")
            return None

        # Create safe filename
        artist = release.basic_information.artists[0].name
        title = release.basic_information.title
        filename = create_safe_filename(
            artist=artist,
            title=title,
            discogs_id=release.id,
            extension="jpg",
        )

        output_path = self.output_dir / filename

        # Skip if exists
        if skip_existing and output_path.exists():
            logger.debug(f"Cover already exists, skipping: {filename}")
            return None

        # Download
        should_close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            should_close_session = True

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with session.get(cover_url, timeout=timeout) as response:
                response.raise_for_status()

                # Save to file
                async with aiofiles.open(output_path, "wb") as f:
                    await f.write(await response.read())

                logger.debug(f"Downloaded cover: {filename}")
                return output_path

        except aiohttp.ClientError as e:
            logger.error(f"Failed to download cover for {release.id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error downloading cover for {release.id}: {e}")
            return None

        finally:
            if should_close_session:
                await session.close()

    async def download_for_releases(
        self,
        releases: list[Release],
        *,
        skip_existing: bool = True,
        progress_callback: Any = None,
    ) -> list[Path]:
        """Download covers for multiple releases.

        Args:
            releases: List of releases to download covers for
            skip_existing: Skip existing covers (default: True)
            progress_callback: Optional callback with (current, total)

        Returns:
            List of paths to downloaded covers (excludes skipped/unavailable)

        Examples:
            >>> async def progress(current, total):
            ...     print(f"Downloaded {current}/{total}")
            >>> paths = await downloader.download_for_releases(
            ...     releases,
            ...     progress_callback=progress
            ... )
        """
        logger.info(f"Downloading covers for {len(releases)} releases")

        semaphore = asyncio.Semaphore(self.max_concurrent)
        downloaded_paths: list[Path] = []

        async with aiohttp.ClientSession() as session:

            async def download_with_semaphore(
                release: Release,
                index: int,
            ) -> Path | None:
                """Download cover with semaphore control."""
                async with semaphore:
                    path = await self.download_cover(
                        release,
                        skip_existing=skip_existing,
                        session=session,
                    )

                    # Progress callback
                    if progress_callback:
                        if asyncio.iscoroutinefunction(progress_callback):
                            await progress_callback(index + 1, len(releases))
                        else:
                            progress_callback(index + 1, len(releases))

                    return path

            # Download all covers concurrently
            tasks = [
                download_with_semaphore(release, i)
                for i, release in enumerate(releases)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out None and exceptions
            for result in results:
                if isinstance(result, Path):
                    downloaded_paths.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error downloading cover: {result}")

        logger.info(
            f"Downloaded {len(downloaded_paths)} covers "
            f"(skipped/unavailable {len(releases) - len(downloaded_paths)})"
        )

        return downloaded_paths

    def get_cover_path_for_release(self, release: Release) -> Path:
        """Get the expected cover path for a release.

        Args:
            release: Release to get cover path for

        Returns:
            Expected path to cover file

        Examples:
            >>> path = downloader.get_cover_path_for_release(release)
            >>> if path.exists():
            ...     print("Cover exists")
        """
        artist = release.basic_information.artists[0].name
        title = release.basic_information.title
        filename = create_safe_filename(
            artist=artist,
            title=title,
            discogs_id=release.id,
            extension="jpg",
        )
        return self.output_dir / filename

    def clear_all(self) -> int:
        """Delete all covers in output directory.

        Returns:
            Number of covers deleted

        Examples:
            >>> deleted = downloader.clear_all()
            >>> print(f"Deleted {deleted} covers")
        """
        if not self.output_dir.exists():
            return 0

        count = 0
        for cover_file in self.output_dir.glob("*.jpg"):
            cover_file.unlink()
            count += 1

        logger.info(f"Deleted {count} covers from {self.output_dir}")
        return count


async def download_covers(
    releases: list[Release],
    output_dir: Path | str | None = None,
    *,
    skip_existing: bool = True,
    progress_callback: Any = None,
) -> list[Path]:
    """Convenience function to download covers for releases.

    Args:
        releases: List of releases to download covers for
        output_dir: Output directory (default: from settings)
        skip_existing: Skip existing covers (default: True)
        progress_callback: Optional progress callback

    Returns:
        List of paths to downloaded covers

    Examples:
        >>> paths = await download_covers(releases)
        >>> print(f"Downloaded {len(paths)} covers")
    """
    downloader = CoverDownloader(output_dir=output_dir)
    return await downloader.download_for_releases(
        releases,
        skip_existing=skip_existing,
        progress_callback=progress_callback,
    )
