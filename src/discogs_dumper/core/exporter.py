"""Export collection data to Excel and CSV formats.

Converts Discogs release data to pandas DataFrames and exports to
Excel (.xlsx) or CSV (.csv) files with customizable column selection.
"""

from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from discogs_dumper.api.models import Release
from discogs_dumper.config.defaults import (
    COLUMN_ALBUM_TITLE,
    COLUMN_ARTIST,
    COLUMN_CATALOG_NUMBER,
    COLUMN_COVER_URL,
    COLUMN_DATE_ADDED,
    COLUMN_DISCOGS_ID,
    COLUMN_DISCOGS_URL,
    COLUMN_FORMAT,
    COLUMN_GENRES,
    COLUMN_LABEL,
    COLUMN_QR_URL,
    COLUMN_RATING,
    COLUMN_STYLES,
    COLUMN_YEAR,
    CSV_EXTENSION,
    DEFAULT_OUTPUT_FILENAME,
    EXCEL_EXTENSION,
)
from discogs_dumper.config.settings import settings
from discogs_dumper.utils.sanitization import sanitize_styles


class CollectionExporter:
    """Exports collection data to various formats.

    Converts Discogs release data to pandas DataFrames and exports
    to Excel or CSV files with configurable columns.

    Examples:
        >>> exporter = CollectionExporter()
        >>> df = exporter.to_dataframe(releases)
        >>> exporter.to_excel(df, "my_collection.xlsx")
    """

    def __init__(self) -> None:
        """Initialize collection exporter."""
        pass

    def to_dataframe(
        self,
        releases: list[Release],
        *,
        include_qr_url: bool = False,
        include_cover_url: bool = False,
        qr_server_url: str | None = None,
    ) -> pd.DataFrame:
        """Convert releases to pandas DataFrame.

        Args:
            releases: List of releases to convert
            include_qr_url: Include QR code URL column (default: False)
            include_cover_url: Include cover art URL column (default: False)
            qr_server_url: Base URL for QR server (e.g., http://localhost:1224)

        Returns:
            DataFrame with release data

        Examples:
            >>> df = exporter.to_dataframe(releases, include_qr_url=True)
            >>> print(df.columns)
        """
        logger.info(f"Converting {len(releases)} releases to DataFrame")

        rows: list[dict[str, Any]] = []

        for release in releases:
            basic_info = release.basic_information

            # Extract artist (first artist if multiple)
            artist = basic_info.artists[0].name if basic_info.artists else "Unknown"

            # Extract label (first label if multiple)
            label = basic_info.labels[0].name if basic_info.labels else ""
            catalog_number = (
                basic_info.labels[0].catno if basic_info.labels else ""
            )

            # Extract format (join multiple formats)
            formats = ", ".join(
                f"{fmt.name} ({fmt.qty}x)" if fmt.qty and fmt.qty > 1 else fmt.name
                for fmt in basic_info.formats
            )

            # Extract genres and styles
            genres = ", ".join(basic_info.genres)
            styles = sanitize_styles(str(basic_info.styles))

            # Create row
            row = {
                COLUMN_DISCOGS_ID: release.id,
                COLUMN_ARTIST: artist,
                COLUMN_ALBUM_TITLE: basic_info.title,
                COLUMN_YEAR: basic_info.year,
                COLUMN_LABEL: label,
                COLUMN_CATALOG_NUMBER: catalog_number,
                COLUMN_FORMAT: formats,
                COLUMN_GENRES: genres,
                COLUMN_STYLES: styles,
                COLUMN_DATE_ADDED: release.date_added.strftime("%Y-%m-%d %H:%M:%S"),
                COLUMN_RATING: release.rating,
                COLUMN_DISCOGS_URL: release.discogs_webpage,
            }

            # Optional: Cover URL
            if include_cover_url:
                cover_url = (
                    basic_info.cover_image_urls.primary
                    or basic_info.cover_image_urls.secondary
                    or ""
                )
                row[COLUMN_COVER_URL] = cover_url

            # Optional: QR URL
            if include_qr_url and qr_server_url:
                # QR filename format: {discogs_id}_{artist}-{title}.png
                from discogs_dumper.utils.sanitization import sanitize_for_filename

                safe_artist = sanitize_for_filename(artist)
                safe_title = sanitize_for_filename(basic_info.title)
                qr_filename = f"{release.id}_{safe_artist}-{safe_title}.png"
                row[COLUMN_QR_URL] = f"{qr_server_url}/{qr_filename}"

            rows.append(row)

        df = pd.DataFrame(rows)

        logger.info(f"Created DataFrame with {len(df)} rows, {len(df.columns)} columns")
        return df

    def to_excel(
        self,
        df: pd.DataFrame,
        output_path: Path | str,
        *,
        sheet_name: str = "Collection",
    ) -> Path:
        """Export DataFrame to Excel file.

        Args:
            df: DataFrame to export
            output_path: Path to output Excel file
            sheet_name: Name of Excel sheet (default: "Collection")

        Returns:
            Path to created Excel file

        Examples:
            >>> path = exporter.to_excel(df, "my_collection.xlsx")
            >>> print(f"Exported to {path}")
        """
        output_path = Path(output_path)

        # Ensure .xlsx extension
        if output_path.suffix != EXCEL_EXTENSION:
            output_path = output_path.with_suffix(EXCEL_EXTENSION)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting to Excel: {output_path}")

        # Export using configured engine
        with pd.ExcelWriter(
            output_path,
            engine=settings.excel_engine,
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(
            f"Successfully exported {len(df)} rows to Excel: {output_path.name}"
        )
        return output_path

    def to_csv(
        self,
        df: pd.DataFrame,
        output_path: Path | str,
        *,
        delimiter: str | None = None,
    ) -> Path:
        """Export DataFrame to CSV file.

        Args:
            df: DataFrame to export
            output_path: Path to output CSV file
            delimiter: CSV delimiter (default: tab from settings)

        Returns:
            Path to created CSV file

        Examples:
            >>> path = exporter.to_csv(df, "my_collection.csv")
            >>> print(f"Exported to {path}")
        """
        output_path = Path(output_path)

        # Ensure .csv extension
        if output_path.suffix != CSV_EXTENSION:
            output_path = output_path.with_suffix(CSV_EXTENSION)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use delimiter from settings if not provided
        if delimiter is None:
            delimiter = settings.csv_delimiter

        logger.info(f"Exporting to CSV: {output_path}")

        df.to_csv(output_path, sep=delimiter, index=False, encoding="utf-8")

        logger.info(f"Successfully exported {len(df)} rows to CSV: {output_path.name}")
        return output_path

    def export(
        self,
        releases: list[Release],
        output_path: Path | str,
        *,
        format: str = "excel",
        include_qr_url: bool = False,
        include_cover_url: bool = False,
        qr_server_url: str | None = None,
    ) -> Path:
        """Export releases to file (convenience method).

        Args:
            releases: List of releases to export
            output_path: Path to output file
            format: Export format ("excel" or "csv")
            include_qr_url: Include QR code URL column (default: False)
            include_cover_url: Include cover art URL column (default: False)
            qr_server_url: Base URL for QR server

        Returns:
            Path to created export file

        Raises:
            ValueError: If format is not "excel" or "csv"

        Examples:
            >>> path = exporter.export(
            ...     releases,
            ...     "collection.xlsx",
            ...     format="excel",
            ...     include_qr_url=True,
            ...     qr_server_url="http://localhost:1224"
            ... )
        """
        # Convert to DataFrame
        df = self.to_dataframe(
            releases,
            include_qr_url=include_qr_url,
            include_cover_url=include_cover_url,
            qr_server_url=qr_server_url,
        )

        # Export based on format
        if format.lower() == "excel":
            return self.to_excel(df, output_path)
        elif format.lower() == "csv":
            return self.to_csv(df, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'excel' or 'csv'.")


def export_collection(
    releases: list[Release],
    output_path: Path | str | None = None,
    *,
    format: str = "excel",
    include_qr_url: bool = False,
    include_cover_url: bool = False,
    qr_server_url: str | None = None,
) -> Path:
    """Convenience function to export collection.

    Args:
        releases: List of releases to export
        output_path: Path to output file (default: discogs_collection.xlsx/.csv)
        format: Export format ("excel" or "csv")
        include_qr_url: Include QR code URL column
        include_cover_url: Include cover art URL column
        qr_server_url: Base URL for QR server

    Returns:
        Path to created export file

    Examples:
        >>> path = export_collection(releases, format="excel")
        >>> print(f"Exported to {path}")
    """
    # Default output path
    if output_path is None:
        extension = EXCEL_EXTENSION if format == "excel" else CSV_EXTENSION
        output_path = Path(DEFAULT_OUTPUT_FILENAME).with_suffix(extension)

    exporter = CollectionExporter()
    return exporter.export(
        releases,
        output_path,
        format=format,
        include_qr_url=include_qr_url,
        include_cover_url=include_cover_url,
        qr_server_url=qr_server_url,
    )
