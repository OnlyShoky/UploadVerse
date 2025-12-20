# CLI Commands

> All commands require `pip install -e .` first to register the `video-publisher` command.

## Available Commands

### `video-publisher upload`

Upload one or more videos to platforms.

```bash
# Auto-detect platform based on aspect ratio
video-publisher upload video.mp4

# Specify platform
video-publisher upload video.mp4 --platforms youtube
video-publisher upload video.mp4 --platforms tiktok,instagram

# With thumbnail and metadata
video-publisher upload video.mp4 \
  --platforms instagram \
  --thumbnail cover.jpg \
  --metadata metadata.json

# Batch upload (all in one browser session)
video-publisher upload vids/*.mp4 --platforms tiktok
```

**Options:**
- `--platforms`, `-p`: Comma-separated platforms (`youtube`, `tiktok`, `instagram`) or `all`.
- `--metadata`, `-m`: Path to a `.json` file or a comma-separated list of files for batch mapping.
- `--thumbnail`: Path to a `.jpg`/`.png` file or a comma-separated list for batch mapping.
- `--headless` / `--no-headless`: Run browser in background (default) or visible.
- `--publish-now`: Publish immediately (overrides scheduling).
- `--scheduled-time`: Schedule publication (ISO 8601 format, e.g., "2025-12-25T10:00:00").
- `--dry-run`: Simulate the upload process without actually clicking the final "Post" button.

---

### `video-publisher metadata`

Manage video metadata (export, template, validate).

```bash
# Generate template
video-publisher metadata template --output template.json

# Export metadata
video-publisher metadata export \
  --title "My Video" \
  --description "Description" \
  --output metadata.json
```

---

### `video-publisher auth`

Authenticate with a platform to save persistent sessions.

```bash
video-publisher auth youtube
video-publisher auth tiktok
video-publisher auth instagram
```

---

### `video-publisher status`

Show authentication status, daily usage, and rate limits.

```bash
video-publisher status
```

---

## 🚀 Advanced Usage & Batching

### 1. Batch Upload (Session Reuse)
When uploading multiple videos, the tool reuses the same browser instance for **TikTok** and **Instagram**. This avoids repeated logins and significantly speeds up the process.

```bash
# Upload 3 videos to TikTok in one session
video-publisher upload vid1.mp4 vid2.mp4 vid3.mp4 --platforms tiktok
```

### 2. Auto-Discovery
If you don't provide `--metadata` or `--thumbnail`, the tool looks for files with the **same basename** as the video:
- `video1.mp4` → Looks for `video1.json` and `video1.jpg`.

### 3. Explicit Mapping
For more control, provide comma-separated lists. They are matched by order:
```bash
video-publisher upload v1.mp4 v2.mp4 \
  --metadata "m1.json,m2.json" \
  --thumbnail "t1.jpg,t2.jpg"
```

### 4. Headless vs Headful
By default, browser-based platforms (TikTok/Instagram) run in **headless** mode (hidden).
- If you need to solve a CAPTCHA or want to watch the process:
```bash
video-publisher upload video.mp4 --no-headless
```
- You can change the default in your `.env` file: `HEADLESS=false`.

---

## Platform Specifics

| Platform | Authentication | Features Supported |
|----------|----------------|---------------------|
| **YouTube** | Official OAuth2 | Title, Desc, Tags, Scheduling |
| **TikTok** | Browser Session | Caption, Tags, Thumbnail, Scheduling |
| **Instagram** | Browser Session | Caption, Tags, Thumbnail, Crop |

---

## 🔧 Troubleshooting

1. **Authentication Expired**: run `video-publisher auth <platform>` again.
2. **Crop Issues (Instagram)**: Instagram sometimes requires manual selection if the auto-crop fails. Use `--no-headless` to see what's happening.
3. **Rate Limits**: Check `video-publisher status` to see if you've hit platform limits for the day.
