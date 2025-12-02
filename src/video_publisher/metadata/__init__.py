"""
Metadata module for JSON import/export of video metadata.
"""
from .handler import (
    export_metadata,
    import_metadata,
    generate_template,
    validate_metadata,
    filter_for_platform,
    merge_metadata
)
from .schema import METADATA_SCHEMA, PLATFORM_FIELDS

__all__ = [
    'export_metadata',
    'import_metadata',
    'generate_template',
    'validate_metadata',
    'filter_for_platform',
    'merge_metadata',
    'METADATA_SCHEMA',
    'PLATFORM_FIELDS'
]
