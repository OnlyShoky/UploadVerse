# Metadata JSON Format

Complete specification for video metadata JSON files used by UploadVerse.

---

## JSON Schema

```json
{
  "title": "string",
  "description": "string",
  "tags": ["array", "of", "strings"],
  "playlist_id": "string (YouTube only)",
  "category_id": "string (YouTube only)",
  "language": "string (ISO 639-1)",
  "privacy_status": "public|private|unlisted",
  "language": "string (ISO 639-1)",
  "privacy_status": "public|private|unlisted",
  "metadata_generated_at": "ISO 8601 timestamp",
  "scheduling": {
    "publish_now": false,
    "scheduled_time": "ISO 8601 timestamp (optional)"
  }
}
```

---

## Field Descriptions

### `title` (string, optional)
- **Description:** Video title
- **Max length:** 100 characters
- **Used by:** YouTube, TikTok (truncated), Instagram (truncated)
- **Example:** `"Surah Al-Ikhlaas [112] | Holy Quran"`

### `description` (string, optional)
- **Description:** Video description/caption
- **Max length:** 5000 characters
- **Used by:** YouTube (description), TikTok (caption), Instagram (caption)
- **Example:**
```
"Surah Al-Ikhlaas [112] | Holy Quran | Mahmoud Khalil Al Hussary | English

Listen and memorize the complete recitation..."
```

### `tags` (array of strings, optional)
- **Description:** Video tags/keywords
- **Max items:** 50
- **Used by:** YouTube (tags), TikTok (converted to hashtags), Instagram (converted to hashtags)
- **Example:**
```json
["Holy Quran", "Quran Recitation", "Hussary", "English", "USA", "UK"]
```

### `playlist_id` (string, optional)
- **Description:** YouTube playlist ID to add video to
- **Used by:** YouTube only (ignored by other platforms)
- **Example:** `"PLR1ei1r7x7pEsxKz2omWk7hWvRemeWcIC"`

### `category_id` (string, optional)
- **Description:** YouTube category ID
- **Used by:** YouTube only
- **Default:** `"22"` (People & Blogs)
- **Common values:**
  - `"10"` - Music
  - `"22"` - People & Blogs
  - `"24"` - Entertainment
  - `"27"` - Education
- **Example:** `"10"`

### `language` (string, optional)
- **Description:** Video language (ISO 639-1 code)
- **Pattern:** Two lowercase letters
- **Default:** `"en"`
- **Used by:** YouTube
- **Examples:** `"en"`, `"es"`, `"fr"`, `"ar"`

### `privacy_status` (string, optional)
- **Description:** Video privacy setting
- **Values:** `"public"`, `"private"`, `"unlisted"`
- **Default:** `"public"`
- **Used by:** YouTube only
- **Example:** `"private"`

### `metadata_generated_at` (string, automatic)
- **Description:** Timestamp when metadata was generated
- **Format:** ISO 8601 with timezone
- **Auto-generated:** Automatically added on export
- **Example:** `"2025-12-02T19:12:32.767512+00:00"`

### `scheduling` (object, optional)
- **Description:** Scheduling configuration
- **Fields:**
  - `publish_now` (boolean): If true, publish immediately (default: false)
  - `scheduled_time` (string): ISO 8601 timestamp for scheduled publication
- **Used by:** YouTube (sets privacy to private until time), TikTok/Instagram (ignored/publish now)
- **Example:**
```json
{
  "publish_now": false,
  "scheduled_time": "2025-12-25T10:00:00Z"
}
```

---

## Complete Example

```json
{
  "title": "Surah Al-Ikhlaas [112] | Holy Quran | Mahmoud Khalil Al Hussary",
  "description": "Surah Al-Ikhlaas [112] | Holy Quran | Mahmoud Khalil Al Hussary | English\n\nListen and memorize the complete recitation of Surah Al-Ikhlaas with clear Arabic verses and English translation.",
  "tags": [
    "Holy Quran",
    "Quran Recitation",
    "Hussary",
    "Mahmoud Khalil Al Hussary",
    "Complete Quran",
    "Quran Playlist",
    "Arabic Quran",
    "Quran With Translation",
    "Quran In Arabic",
    "Quran In English",
    "Quran",
    "English",
    "USA",
    "UK"
  ],
  "playlist_id": "PLR1ei1r7x7pEsxKz2omWk7hWvRemeWcIC",
  "category_id": "10",
  "language": "en",
  "privacy_status": "public",
  "privacy_status": "public",
  "metadata_generated_at": "2025-12-02T19:12:32.767512+00:00",
  "scheduling": {
    "publish_now": false,
    "scheduled_time": "2025-12-25T10:00:00Z"
  }
}
```

---

## Platform-Specific Field Mapping

### YouTube
**Supported fields:**
- `title` → YouTube title
- `description` → YouTube description
- `tags` → YouTube tags (array)
- `playlist_id` → Add to playlist
- `category_id` → YouTube category
- `language` → Video language
- `privacy_status` → Privacy setting

### TikTok
**Supported fields:**
- `description` → TikTok caption
- `tags` → Converted to hashtags

**Conversion example:**
```json
{
  "description": "Amazing video!",
  "tags": ["music", "dance", "viral"]
}
```
Becomes:
```
Caption: "Amazing video! #music #dance #viral"
```

### Instagram
**Supported fields:**
- `description` → Instagram caption
- `tags` → Converted to hashtags

**Conversion example:**
```json
{
  "description": "Check this out!",
  "tags": ["reels", "viral", "trending"]
}
```
Becomes:
```
Caption: "Check this out! #reels #viral #trending"
```

---

## Validation Rules

### Required Fields
**None** - All fields are optional

### Constraints
- `title`: 1-100 characters
- `description`: Max 5000 characters
- `tags`: Max 50 items
- `language`: Must be 2-letter ISO 639-1 code (e.g., "en", "es")
- `privacy_status`: Must be "public", "private", or "unlisted"
- No additional properties allowed

### Validation Errors

**Invalid JSON:**
```json
{
  "title": "Test"
  "description": "Missing comma"  // Error: Invalid JSON syntax
}
```

**Invalid privacy_status:**
```json
{
  "privacy_status": "secret"  // Error: Must be public, private, or unlisted
}
```

**Title too long:**
```json
{
  "title": "A".repeat(101)  // Error: Max 100 characters
}
```

---

## Usage Examples

### Generate Template

**CLI:**
```bash
video-publisher metadata template --output template.json
```

**API:**
```bash
curl http://localhost:5000/api/metadata/template
```

**Python:**
```python
from video_publisher.metadata import generate_template
template = generate_template()
```

---

### Export Metadata

**CLI:**
```bash
video-publisher metadata export \
  --title "My Video" \
  --description "Video description" \
  --tags "tag1,tag2,tag3" \
  --output my_metadata.json
```

**API:**
```bash
curl -X POST http://localhost:5000/api/metadata/export \
  -H "Content-Type: application/json" \
  -d '{"title": "My Video", "description": "Description"}' \
  --output metadata.json
```

**Python:**
```python
from video_publisher.metadata import export_metadata

metadata = {
    "title": "My Video",
    "description": "Description",
    "tags": ["tag1", "tag2"]
}

export_metadata(metadata, "metadata.json")
```

---

### Import and Use

**CLI:**
```bash
video-publisher upload video.mp4 --metadata metadata.json --platforms youtube
```

**API:**
```bash
curl -X POST http://localhost:5000/api/metadata/import \
  -F "metadata=@metadata.json"
```

**Python:**
```python
from video_publisher.metadata import import_metadata

metadata = import_metadata("metadata.json")
# Use with upload
```

---

### Validate

**CLI:**
```bash
video-publisher metadata validate --input metadata.json
```

**Python:**
```python
from video_publisher.metadata import import_metadata

try:
    metadata = import_metadata("metadata.json")
    print("✓ Valid metadata")
except ValueError as e:
    print(f"✗ Invalid: {e}")
```

---

## Best Practices

### 1. Use Templates
Start with a template rather than creating from scratch:
```bash
video-publisher metadata template --output base.json
# Edit base.json with your data
```

### 2. Validate Before Upload
Always validate metadata files before using:
```bash
video-publisher metadata validate --input my_metadata.json
```

### 3. Platform-Specific Exports
Create separate metadata files for different platforms if needed:
```bash
# YouTube with all fields
video-publisher metadata export \
  --title "Full Title" \
  --playlist-id "PLxxx" \
  --category-id "10" \
  --output youtube_meta.json

# TikTok/Instagram (simpler)
video-publisher metadata export \
  --description "Short caption" \
  --tags "viral,trending" \
  --output tiktok_meta.json
```

### 4. UTF-8 Encoding
Always use UTF-8 encoding for non-English text:
```json
{
  "title": "السلام عليكم",
  "description": "مرحبا بكم"
}
```

### 5. Version Control
Store metadata JSON files in Git for tracking changes:
```bash
git add metadata/*.json
git commit -m "Update video metadata"
```

---

## Troubleshooting

### "Invalid JSON file"
**Problem:** Syntax error in JSON

**Solution:**
- Use a JSON validator (jsonlint.com)
- Check for missing commas, quotes, brackets

### "Invalid metadata: privacy_status"
**Problem:** Invalid enum value

**Solution:**
Use only: `"public"`, `"private"`, or `"unlisted"`

### "Field not used by platform"
**Problem:** Using YouTube-specific field for TikTok

**Solution:**
This is not an error - fields are automatically filtered per platform. YouTube-only fields (playlist_id, category_id) are ignored by TikTok/Instagram.

---

## See Also

- [CLI Usage](cli_usage.md) - CLI commands
- [YouTube Setup](youtube_setup.md) - YouTube configuration
- [TikTok Setup](tiktok_setup.md) - TikTok configuration
- [Instagram Setup](instagram_setup.md) - Instagram configuration
