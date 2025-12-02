# CLI Commands

> All commands require `pip install -e .` first to register the `video-publisher` command.

## Available Commands

### `video-publisher upload`

Upload a video to platforms.

```bash
# Auto-detect platform based on aspect ratio
video-publisher upload video.mp4

# Specify platform
video-publisher upload video.mp4 --platforms youtube
video-publisher upload video.mp4 --platforms tiktok
video-publisher upload video.mp4 --platforms instagram

# Multiple platforms
video-publisher upload video.mp4 --platforms youtube,tiktok

# With metadata
video-publisher upload video.mp4 \
  --platforms youtube \
  --title "My Video" \
  --description "Video description" \
  --tags "tag1,tag2,tag3"
```

**Options:**
- `--platforms`, `-p`: Comma-separated platforms or 'all'
- `--title`, `-t`: Video title
- `--description`, `-d`: Video description  
- `--tags`: Comma-separated tags

---

### `video-publisher auth`

Authenticate with a platform.

```bash
# YouTube
video-publisher auth youtube

# TikTok
video-publisher auth tiktok

# Instagram
video-publisher auth instagram
```

**What it does:**
- Opens browser for authentication
- Saves session/tokens to `data/sessions/`

---

### `video-publisher status`

Show platform authentication status and rate limits.

```bash
video-publisher status
```

**Output shows:**
- Authentication status for each platform
- Daily upload usage
- Remaining uploads

---

### `video-publisher version`

Show version information.

```bash
video-publisher version
```

---

## Usage Examples

### First Time Setup

```bash
# 1. Install
pip install -e .

# 2. Authenticate YouTube
video-publisher auth youtube

# 3. Check status
video-publisher status

# 4. Upload
video-publisher upload my_video.mp4 --platforms youtube
```

### Upload to Multiple Platforms

```bash
# Authenticate each platform first
video-publisher auth youtube
video-publisher auth tiktok

# Upload to both
video-publisher upload video.mp4 --platforms youtube,tiktok
```

### Auto-Detection

```bash
# 16:9 video → Auto routes to YouTube
video-publisher upload horizontal.mp4

# 9:16 video → Auto routes to TikTok, Instagram
video-publisher upload vertical.mp4
```

---

## Platform-Specific Notes

**YouTube:**
- Uses official API
- Safe and reliable
- Supports title, description, tags

**TikTok:**
- Browser automation
- Violates TOS
- May require solving CAPTCHAs
- Use test accounts only

**Instagram:**
- Browser automation
- Violates TOS
- High ban risk
- Requires 9:16 vertical videos
- Use test accounts only

---

## Error Handling

If upload fails, check:
1. Authentication: `video-publisher status`
2. Video format (must be .mp4, .mov, .avi, etc.)
3. Internet connection
4. Platform rate limits

Re-authenticate if needed:
```bash
video-publisher auth youtube  # or tiktok/instagram
```
