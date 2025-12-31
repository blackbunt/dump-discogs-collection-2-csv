"""Unit tests for sanitization utilities."""

import pytest

from discogs_dumper.utils.sanitization import (
    create_safe_filename,
    sanitize_artist,
    sanitize_artist_for_url,
    sanitize_for_filename,
    sanitize_for_url,
    sanitize_styles,
    sanitize_title,
    sanitize_title_for_url,
    truncate_filename,
)


class TestSanitizeArtist:
    """Tests for sanitize_artist function."""

    def test_artist_without_number(self) -> None:
        """Test artist name without Discogs numbering."""
        assert sanitize_artist("The Beatles") == "The Beatles"
        assert sanitize_artist("Pink Floyd") == "Pink Floyd"

    def test_artist_with_number(self) -> None:
        """Test removing Discogs numbering from artist names."""
        assert sanitize_artist("Prince (2)") == "Prince"
        assert sanitize_artist("Madonna (3)") == "Madonna"
        assert sanitize_artist("Artist (10)") == "Artist"

    def test_artist_with_trailing_spaces(self) -> None:
        """Test that trailing spaces are removed."""
        assert sanitize_artist("The Who (2)  ") == "The Who"

    def test_artist_number_in_middle(self) -> None:
        """Test that numbers in the middle are not removed."""
        assert sanitize_artist("Blink-182") == "Blink-182"
        assert sanitize_artist("Studio (54) Band") == "Studio (54) Band"


class TestSanitizeTitle:
    """Tests for sanitize_title function."""

    def test_title_with_slash(self) -> None:
        """Test replacing slash-space-slash with hyphen."""
        assert sanitize_title("Dark Side / Of The Moon") == "Dark Side-Of The Moon"

    def test_title_with_number(self) -> None:
        """Test removing trailing Discogs numbering."""
        assert sanitize_title("Album Title (2)") == "Album Title"

    def test_title_with_special_chars(self) -> None:
        """Test handling special characters."""
        result = sanitize_title("Title: The Subtitle!")
        assert "/" not in result
        assert result  # Should not be empty

    def test_simple_title(self) -> None:
        """Test simple title without special characters."""
        assert sanitize_title("Abbey Road") == "Abbey Road"


class TestSanitizeForFilename:
    """Tests for sanitize_for_filename function."""

    def test_simple_filename(self) -> None:
        """Test simple filename without special characters."""
        assert sanitize_for_filename("simple_filename") == "simple_filename"

    def test_forbidden_characters(self) -> None:
        """Test replacement of forbidden filename characters."""
        result = sanitize_for_filename('test<>:"/\\|?*file')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "/" not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_spaces_replaced(self) -> None:
        """Test that spaces are replaced with underscores."""
        assert sanitize_for_filename("file with spaces") == "file_with_spaces"

    def test_multiple_underscores(self) -> None:
        """Test that multiple underscores are collapsed."""
        assert sanitize_for_filename("file___name") == "file_name"

    def test_leading_trailing_cleanup(self) -> None:
        """Test removal of leading/trailing underscores and hyphens."""
        assert sanitize_for_filename("_-filename-_") == "filename"

    def test_length_limit(self) -> None:
        """Test filename length is limited to 255 characters."""
        long_name = "a" * 300
        result = sanitize_for_filename(long_name)
        assert len(result) <= 255


class TestSanitizeForUrl:
    """Tests for sanitize_for_url function."""

    def test_spaces_to_hyphens(self) -> None:
        """Test spaces are replaced with hyphens."""
        assert sanitize_for_url("The Beatles") == "The-Beatles"

    def test_slash_replacement(self) -> None:
        """Test slash-space-slash replacement."""
        assert sanitize_for_url("Pink Floyd / Dark Side") == "Pink-Floyd-Dark-Side"

    def test_hash_removal(self) -> None:
        """Test hash symbols are removed."""
        assert "#" not in sanitize_for_url("Track #1")

    def test_multiple_hyphens(self) -> None:
        """Test multiple hyphens are collapsed."""
        assert sanitize_for_url("test---url") == "test-url"

    def test_leading_trailing_hyphens(self) -> None:
        """Test leading/trailing hyphens are removed."""
        assert sanitize_for_url("-url-") == "url"


class TestSanitizeArtistForUrl:
    """Tests for sanitize_artist_for_url function."""

    def test_combines_artist_and_url_sanitization(self) -> None:
        """Test that it combines both sanitization steps."""
        assert sanitize_artist_for_url("The Beatles (2)") == "The-Beatles"
        assert sanitize_artist_for_url("Artist Name (3)") == "Artist-Name"


class TestSanitizeTitleForUrl:
    """Tests for sanitize_title_for_url function."""

    def test_combines_title_and_url_sanitization(self) -> None:
        """Test that it combines both sanitization steps."""
        result = sanitize_title_for_url("Dark Side / Of The Moon (2)")
        assert "Dark" in result
        assert "Side" in result
        assert " " not in result
        assert "/" not in result


class TestSanitizeStyles:
    """Tests for sanitize_styles function."""

    def test_removes_brackets_and_quotes(self) -> None:
        """Test removal of brackets and quotes."""
        assert sanitize_styles("['Rock', 'Alternative']") == "Rock, Alternative"

    def test_single_style(self) -> None:
        """Test single style in list."""
        assert sanitize_styles("['Electronic']") == "Electronic"

    def test_empty_list(self) -> None:
        """Test empty list."""
        assert sanitize_styles("[]") == ""


class TestCreateSafeFilename:
    """Tests for create_safe_filename function."""

    def test_basic_filename(self) -> None:
        """Test basic filename creation."""
        result = create_safe_filename("The Beatles", "Abbey Road", 123456)
        assert result == "123456_The_Beatles-Abbey_Road.jpg"

    def test_custom_extension(self) -> None:
        """Test with custom extension."""
        result = create_safe_filename("Artist", "Title", 789, "png")
        assert result.endswith(".png")
        assert "789" in result

    def test_special_characters_sanitized(self) -> None:
        """Test that special characters are sanitized."""
        result = create_safe_filename("Artist / Name", "Title: Subtitle", 456)
        assert "/" not in result
        assert ":" not in result

    def test_discogs_id_as_string(self) -> None:
        """Test that Discogs ID can be passed as string."""
        result = create_safe_filename("Artist", "Title", "123")
        assert result.startswith("123_")


class TestTruncateFilename:
    """Tests for truncate_filename function."""

    def test_short_filename_unchanged(self) -> None:
        """Test that short filenames are not modified."""
        filename = "short.jpg"
        assert truncate_filename(filename) == filename

    def test_truncation_preserves_extension(self) -> None:
        """Test that extension is preserved when truncating."""
        long_name = "a" * 300 + ".jpg"
        result = truncate_filename(long_name, max_length=20)
        assert result.endswith(".jpg")
        assert len(result) == 20

    def test_truncation_at_max_length(self) -> None:
        """Test truncation at exact max length."""
        result = truncate_filename("very_long_filename.jpg", max_length=20)
        assert len(result) == 20
        assert result.endswith(".jpg")

    def test_filename_without_extension(self) -> None:
        """Test truncation of filename without extension."""
        long_name = "a" * 300
        result = truncate_filename(long_name, max_length=100)
        assert len(result) == 100
        assert "." not in result


class TestSanitizationCaching:
    """Tests for LRU cache on sanitization functions."""

    def test_artist_sanitization_cached(self) -> None:
        """Test that repeated calls use cache."""
        # Call multiple times with same input
        for _ in range(10):
            result = sanitize_artist("The Beatles (2)")
            assert result == "The Beatles"

        # Check cache info (should have hits)
        cache_info = sanitize_artist.cache_info()
        assert cache_info.hits > 0

    def test_different_inputs_cached_separately(self) -> None:
        """Test that different inputs are cached separately."""
        artist1 = sanitize_artist("Artist 1 (2)")
        artist2 = sanitize_artist("Artist 2 (3)")

        assert artist1 == "Artist 1"
        assert artist2 == "Artist 2"

        # Both should be in cache
        cache_info = sanitize_artist.cache_info()
        assert cache_info.currsize >= 2
