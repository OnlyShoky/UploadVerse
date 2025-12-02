"""
Metadata handler for JSON import/export operations.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError

from .schema import METADATA_SCHEMA, PLATFORM_FIELDS, DEFAULT_VALUES


def generate_template() -> Dict[str, Any]:
    """
    Generate an empty metadata template with all fields.
    
    Returns:
        Dictionary with empty/default metadata fields
    """
    return {
        "title": "",
        "description": "",
        "tags": [],
        "playlist_id": "",
        "category_id": DEFAULT_VALUES["category_id"],
        "language": DEFAULT_VALUES["language"],
        "privacy_status": DEFAULT_VALUES["privacy_status"],
        "metadata_generated_at": datetime.now(timezone.utc).isoformat()
    }


def validate_metadata(metadata: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate metadata against JSON schema.
    
    Args:
        metadata: Dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        validate(instance=metadata, schema=METADATA_SCHEMA)
        return True, None
    except ValidationError as e:
        return False, str(e.message)


def export_metadata(metadata: Dict[str, Any], output_path: str) -> None:
    """
    Export metadata dictionary to JSON file.
    
    Args:
        metadata: Metadata dictionary to export
        output_path: Path to output JSON file
        
    Raises:
        ValueError: If metadata validation fails
        IOError: If file write fails
    """
    # Add generation timestamp if not present
    if "metadata_generated_at" not in metadata:
        metadata["metadata_generated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Validate before export
    is_valid, error = validate_metadata(metadata)
    if not is_valid:
        raise ValueError(f"Invalid metadata: {error}")
    
    # Write to file with pretty-print
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def import_metadata(json_path: str) -> Dict[str, Any]:
    """
    Import metadata from JSON file.
    
    Args:
        json_path: Path to JSON file
        
    Returns:
        Validated metadata dictionary
        
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        ValueError: If JSON is invalid or validation fails
    """
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    # Load JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")
    
    # Validate
    is_valid, error = validate_metadata(metadata)
    if not is_valid:
        raise ValueError(f"Invalid metadata: {error}")
    
    return metadata


def filter_for_platform(metadata: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """
    Filter metadata to include only fields supported by the platform.
    
    Args:
        metadata: Full metadata dictionary
        platform: Platform name ('youtube', 'tiktok', 'instagram')
        
    Returns:
        Filtered metadata dictionary with platform-specific field names
    """
    platform = platform.lower()
    
    if platform not in PLATFORM_FIELDS:
        raise ValueError(f"Unknown platform: {platform}")
    
    platform_config = PLATFORM_FIELDS[platform]
    filtered = {}
    
    for field in metadata.keys():
        # Check if field is supported by platform
        if field in platform_config["supported"]:
            # Map to platform-specific field name if needed
            mapped_field = platform_config["field_mapping"].get(field, field)
            value = metadata[field]
            
            # Special handling for tags -> hashtags conversion
            if field == "tags" and mapped_field == "hashtags" and isinstance(value, list):
                # Convert tags list to hashtag string
                filtered[mapped_field] = " ".join(f"#{tag}" for tag in value)
            else:
                filtered[mapped_field] = value
    
    return filtered


def merge_metadata(json_metadata: Dict[str, Any], cli_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge JSON metadata with CLI arguments, with CLI taking precedence.
    
    Args:
        json_metadata: Metadata from JSON file
        cli_metadata: Metadata from CLI arguments
        
    Returns:
        Merged metadata dictionary
    """
    # Start with JSON metadata
    merged = json_metadata.copy()
    
    # Override with CLI arguments (only if CLI value is not None/empty)
    for key, value in cli_metadata.items():
        if value is not None and value != "" and value != []:
            merged[key] = value
    
    return merged
