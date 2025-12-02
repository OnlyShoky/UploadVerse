"""
JSON Schema definition for video metadata.
"""

# JSON Schema for metadata validation
METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "maxLength": 100,
            "description": "Video title"
        },
        "description": {
            "type": "string",
            "maxLength": 5000,
            "description": "Video description"
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 50,
            "description": "Video tags/keywords"
        },
        "playlist_id": {
            "type": "string",
            "description": "YouTube playlist ID (YouTube only)"
        },
        "category_id": {
            "type": "string",
            "description": "YouTube category ID (YouTube only)"
        },
        "language": {
            "type": "string",
            "description": "Language code (ISO 639-1)"
        },
        "privacy_status": {
            "type": "string",
            "enum": ["public", "private", "unlisted"],
            "description": "Privacy setting"
        },
        "metadata_generated_at": {
            "type": "string",
            "description": "Timestamp when metadata was generated"
        }
    },
    "required": [],  # No required fields - all optional
    "additionalProperties": False
}

# Platform-specific field mappings
PLATFORM_FIELDS = {
    "youtube": {
        "supported": [
            "title",
            "description", 
            "tags",
            "playlist_id",
            "category_id",
            "language",
            "privacy_status"
        ],
        "field_mapping": {
            "description": "description",
            "tags": "tags",
            "privacy_status": "privacy_status",
            "category_id": "category_id"
        }
    },
    "tiktok": {
        "supported": [
            "description",  # Used as caption
            "tags"  # Converted to hashtags
        ],
        "field_mapping": {
            "description": "caption",
            "tags": "hashtags"
        }
    },
    "instagram": {
        "supported": [
            "description",  # Used as caption
            "tags"  # Converted to hashtags
        ],
        "field_mapping": {
            "description": "caption",
            "tags": "hashtags"
        }
    }
}

# Default values for metadata fields
DEFAULT_VALUES = {
    "privacy_status": "public",
    "category_id": "22",  # People & Blogs
    "language": "en",
    "tags": []
}
