"""Discogs Collection Dumper - Export your Discogs collection with style.

A modern Python CLI tool for exporting Discogs music collections to Excel/CSV
with QR codes and cover art downloads.
"""

__version__ = "2.0.0"
__author__ = "Bernie"
__license__ = "MIT"

# Public API exports
from discogs_dumper.api.models import (
    Artist,
    BasicInformation,
    CollectionPage,
    CollectionValue,
    Label,
    Pagination,
    Release,
)
from discogs_dumper.persistence.models import CredentialInfo, ExportJob, ProgressState

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    # API Models
    "Artist",
    "BasicInformation",
    "CollectionPage",
    "CollectionValue",
    "Label",
    "Pagination",
    "Release",
    # Persistence Models
    "CredentialInfo",
    "ExportJob",
    "ProgressState",
]
