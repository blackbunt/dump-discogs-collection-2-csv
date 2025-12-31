"""String sanitization utilities for Discogs data.

Provides functions for cleaning up artist names, album titles, and other
strings for use in filenames, URLs, and display.
"""

import re
from functools import lru_cache


@lru_cache(maxsize=1024)
def sanitize_artist(artist: str) -> str:
    """Remove Discogs numbering from artist names.

    Discogs adds numbers to duplicate artist names, e.g., "Artist (2)".
    This function removes those numbers for cleaner display and filenames.

    Args:
        artist: Artist name from Discogs

    Returns:
        Cleaned artist name without trailing numbers

    Examples:
        >>> sanitize_artist("The Beatles")
        'The Beatles'
        >>> sanitize_artist("Prince (2)")
        'Prince'
        >>> sanitize_artist("Madonna (3)")
        'Madonna'
    """
    # Strip whitespace first so regex can match trailing pattern
    cleaned = artist.rstrip()
    # Remove trailing (digits) pattern
    cleaned = re.sub(r"\(\d+\)$", "", cleaned)
    return cleaned.rstrip()


@lru_cache(maxsize=1024)
def sanitize_title(title: str) -> str:
    """Clean release title for filenames and display.

    Removes or replaces problematic characters that can't be used
    in filenames or look bad in display.

    Args:
        title: Release title from Discogs

    Returns:
        Cleaned title safe for filenames

    Examples:
        >>> sanitize_title("Dark Side / Of The Moon")
        'Dark Side-Of The Moon'
        >>> sanitize_title("Album Title (2)")
        'Album Title'
    """
    # Replace slash-space-slash with hyphen
    cleaned = re.sub(r" / ", "-", title)

    # Remove trailing (digits) pattern
    cleaned = re.sub(r"\(\d+\)$", "", cleaned)

    # Replace non-word characters (except hyphens) with hyphen
    cleaned = re.sub(r"\W+(?![^-])", "-", cleaned)

    # Remove trailing hyphens
    cleaned = re.sub(r"-+$", "", cleaned)

    # Replace any remaining slashes with hyphens
    cleaned = re.sub(r"/", "-", cleaned)

    return cleaned.rstrip()


@lru_cache(maxsize=2048)
def sanitize_for_filename(text: str) -> str:
    """Make string safe for use in filenames.

    Removes or replaces characters that are problematic in filenames
    across different operating systems (Windows, macOS, Linux).

    Args:
        text: Input string

    Returns:
        Filename-safe string

    Examples:
        >>> sanitize_for_filename("Artist / Album: The Best")
        'Artist_Album_The_Best'
        >>> sanitize_for_filename('Song "Title" <3>')
        'Song_Title_3'
    """
    # Replace problematic characters with underscore
    # Windows forbidden: < > : " / \ | ? *
    # Also replace spaces for cleaner filenames
    cleaned = re.sub(r'[<>:"/\\|?*\s]', "_", text)

    # Remove control characters
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", cleaned)

    # Replace multiple underscores with single
    cleaned = re.sub(r"_+", "_", cleaned)

    # Remove leading/trailing underscores and hyphens
    cleaned = cleaned.strip("_-")

    # Limit length to 255 characters (filesystem limit)
    if len(cleaned) > 255:
        cleaned = cleaned[:255]

    return cleaned


@lru_cache(maxsize=1024)
def sanitize_for_url(text: str) -> str:
    """Make string safe for use in URLs.

    Converts text to URL-friendly format by replacing spaces and
    special characters with hyphens.

    Args:
        text: Input string

    Returns:
        URL-safe string

    Examples:
        >>> sanitize_for_url("The Beatles")
        'The-Beatles'
        >>> sanitize_for_url("Pink Floyd / Dark Side")
        'Pink-Floyd-Dark-Side'
    """
    # Replace slash-space-slash with hyphen
    cleaned = re.sub(r" / ", "-", text)

    # Replace non-word characters with hyphen
    cleaned = re.sub(r"\W+(?![^-])", "-", text)

    # Remove trailing hyphens
    cleaned = re.sub(r"-+$", "", cleaned)

    # Replace slashes with hyphens
    cleaned = re.sub(r"/", "-", cleaned)

    # Replace spaces with hyphens
    cleaned = re.sub(r"\s+", "-", cleaned)

    # Remove hash symbols
    cleaned = re.sub(r"#", "", cleaned)

    # Replace multiple hyphens with single
    cleaned = re.sub(r"-+", "-", cleaned)

    # Remove leading/trailing hyphens
    cleaned = cleaned.strip("-")

    return cleaned


def sanitize_artist_for_url(artist: str) -> str:
    """Sanitize artist name for URL usage.

    Combines artist sanitization and URL sanitization.

    Args:
        artist: Artist name from Discogs

    Returns:
        URL-safe artist name

    Examples:
        >>> sanitize_artist_for_url("The Beatles (2)")
        'The-Beatles'
    """
    cleaned = sanitize_artist(artist)
    return sanitize_for_url(cleaned)


def sanitize_title_for_url(title: str) -> str:
    """Sanitize release title for URL usage.

    Combines title sanitization and URL sanitization.

    Args:
        title: Release title from Discogs

    Returns:
        URL-safe title

    Examples:
        >>> sanitize_title_for_url("Dark Side / Of The Moon (2)")
        'Dark-Side-Of-The-Moon'
    """
    cleaned = sanitize_title(title)
    return sanitize_for_url(cleaned)


def sanitize_styles(styles: str) -> str:
    """Remove brackets and quotes from styles string.

    Discogs styles are often formatted as lists with brackets and quotes.
    This function cleans them up for display.

    Args:
        styles: Styles string from Discogs (e.g., "['Rock', 'Pop']")

    Returns:
        Cleaned styles string

    Examples:
        >>> sanitize_styles("['Rock', 'Alternative']")
        'Rock, Alternative'
        >>> sanitize_styles("['Electronic']")
        'Electronic'
    """
    cleaned = styles.replace("[", "").replace("]", "").replace("'", "")
    return cleaned.strip()


def create_safe_filename(
    artist: str,
    title: str,
    discogs_id: int | str,
    extension: str = "jpg",
) -> str:
    """Create a safe filename from artist, title, and ID.

    Combines artist and title into a filename with the format:
    {discogs_id}_{artist}-{title}.{extension}

    Args:
        artist: Artist name
        title: Release/album title
        discogs_id: Discogs release ID
        extension: File extension (default: jpg)

    Returns:
        Safe filename

    Examples:
        >>> create_safe_filename("The Beatles", "Abbey Road", 123456)
        '123456_The_Beatles-Abbey_Road.jpg'
        >>> create_safe_filename("Artist / Name", "Title: Subtitle", 789, "png")
        '789_Artist_Name-Title_Subtitle.png'
    """
    safe_artist = sanitize_for_filename(artist)
    safe_title = sanitize_for_filename(title)
    filename = f"{discogs_id}_{safe_artist}-{safe_title}.{extension}"
    return filename


def truncate_filename(filename: str, max_length: int = 255) -> str:
    """Truncate filename to maximum length while preserving extension.

    Args:
        filename: Filename to truncate
        max_length: Maximum length (default: 255, filesystem limit)

    Returns:
        Truncated filename with extension preserved

    Examples:
        >>> truncate_filename("very_long_filename.jpg", 20)
        'very_long_fil.jpg'
    """
    if len(filename) <= max_length:
        return filename

    # Split filename and extension
    if "." in filename:
        name, ext = filename.rsplit(".", 1)
        # Reserve space for extension and dot
        max_name_length = max_length - len(ext) - 1
        truncated = name[:max_name_length] + "." + ext
    else:
        truncated = filename[:max_length]

    return truncated
