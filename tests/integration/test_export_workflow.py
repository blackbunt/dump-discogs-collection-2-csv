"""Integration tests for export workflow.

Tests the complete flow of converting releases to DataFrame and exporting.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone

from discogs_dumper.api.models import (
    Release,
    BasicInformation,
    Artist,
    Label,
    Format,
)
from discogs_dumper.core.exporter import CollectionExporter


@pytest.fixture
def sample_releases():
    """Create sample releases for testing."""
    releases = []

    for i in range(5):
        release = Release(
            id=1000 + i,
            instance_id=2000 + i,
            date_added=datetime(2024, 1, 1 + i, 12, 0, 0, tzinfo=timezone.utc),
            rating=i,
            basic_information=BasicInformation(
                id=1000 + i,
                title=f"Album {i}",
                year=2020 + i,
                artists=[
                    Artist(id=100 + i, name=f"Artist {i}", resource_url=f"https://api.discogs.com/artists/{100+i}"),
                ],
                labels=[
                    Label(id=200 + i, name=f"Label {i}", catno=f"CAT-{i:03d}"),
                ],
                formats=[
                    Format(name="Vinyl", qty="1", descriptions=["LP", "Album"]),
                ],
                genres=["Rock", "Electronic"],
                styles=["Alternative", "Ambient"],
                thumb=f"https://example.com/thumb{i}.jpg",
                cover_image=f"https://example.com/cover{i}.jpg",
            ),
            notes=[],
        )
        releases.append(release)

    return releases


def test_exporter_to_dataframe(sample_releases):
    """Test converting releases to DataFrame."""
    exporter = CollectionExporter()
    df = exporter.to_dataframe(sample_releases)

    # Verify DataFrame structure
    assert len(df) == 5
    assert "discogs_no" in df.columns
    assert "artist" in df.columns
    assert "album_title" in df.columns
    assert "year" in df.columns

    # Verify data
    assert df.iloc[0]["discogs_no"] == 1000
    assert df.iloc[0]["artist"] == "Artist 0"
    assert df.iloc[0]["album_title"] == "Album 0"
    assert df.iloc[0]["year"] == 2020
    assert df.iloc[0]["label"] == "Label 0"
    assert df.iloc[0]["catalog_number"] == "CAT-000"
    assert df.iloc[0]["format"] == "Vinyl"
    assert "Rock, Electronic" in df.iloc[0]["genres"]


def test_exporter_to_dataframe_with_cover_url(sample_releases):
    """Test DataFrame includes cover URL when requested."""
    exporter = CollectionExporter()
    df = exporter.to_dataframe(sample_releases, include_cover_url=True)

    # Verify cover URL column exists
    assert "cover_url" in df.columns
    assert df.iloc[0]["cover_url"] == "https://example.com/cover0.jpg"


def test_exporter_to_dataframe_with_qr_url(sample_releases):
    """Test DataFrame includes QR URL when requested."""
    exporter = CollectionExporter()
    df = exporter.to_dataframe(
        sample_releases,
        include_qr_url=True,
        qr_server_url="http://localhost:1224",
    )

    # Verify QR URL column exists
    assert "qr_url" in df.columns
    assert "http://localhost:1224" in df.iloc[0]["qr_url"]
    assert "1000_Artist_0-Album_0.png" in df.iloc[0]["qr_url"]


def test_exporter_to_excel(sample_releases, tmp_path):
    """Test exporting to Excel file."""
    exporter = CollectionExporter()
    df = exporter.to_dataframe(sample_releases)

    output_path = tmp_path / "test_collection.xlsx"
    result_path = exporter.to_excel(df, output_path)

    # Verify file was created
    assert result_path.exists()
    assert result_path.suffix == ".xlsx"

    # Verify can read it back
    import pandas as pd

    df_read = pd.read_excel(result_path)
    assert len(df_read) == 5
    assert df_read.iloc[0]["discogs_no"] == 1000


def test_exporter_to_csv(sample_releases, tmp_path):
    """Test exporting to CSV file."""
    exporter = CollectionExporter()
    df = exporter.to_dataframe(sample_releases)

    output_path = tmp_path / "test_collection.csv"
    result_path = exporter.to_csv(df, output_path)

    # Verify file was created
    assert result_path.exists()
    assert result_path.suffix == ".csv"

    # Verify can read it back
    import pandas as pd

    df_read = pd.read_csv(result_path, sep="\t")
    assert len(df_read) == 5
    assert df_read.iloc[0]["discogs_no"] == 1000


def test_exporter_export_convenience_function(sample_releases, tmp_path):
    """Test the convenience export() method."""
    exporter = CollectionExporter()

    output_path = tmp_path / "collection"
    result_path = exporter.export(
        sample_releases,
        output_path,
        format="excel",
        include_cover_url=True,
    )

    # Verify file was created with correct extension
    assert result_path.exists()
    assert result_path.suffix == ".xlsx"

    # Verify cover_url column exists by reading back the Excel
    import pandas as pd

    df_read = pd.read_excel(result_path)
    assert "cover_url" in df_read.columns
    assert len(df_read) == 5


def test_exporter_handles_missing_fields(tmp_path):
    """Test exporter handles releases with missing optional fields."""
    # Create release with minimal fields
    release = Release(
        id=1000,
        instance_id=2000,
        date_added=datetime.now(timezone.utc),
        rating=0,
        basic_information=BasicInformation(
            id=1000,
            title="Minimal Album",
            year=2020,
            artists=[],  # No artists
            labels=[],  # No labels
            formats=[],  # No formats
            genres=[],
            styles=[],
            thumb="",
            cover_image="",
        ),
        notes=[],
    )

    exporter = CollectionExporter()
    df = exporter.to_dataframe([release])

    # Should handle gracefully
    assert len(df) == 1
    assert df.iloc[0]["artist"] == "Unknown"  # Default for missing artist
    assert df.iloc[0]["label"] == ""
    assert df.iloc[0]["format"] == ""
