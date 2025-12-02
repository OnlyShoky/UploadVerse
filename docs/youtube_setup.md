# YouTube Setup

## Get Credentials from Google Cloud Console

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable "YouTube Data API v3":
   - APIs & Services → Library → Search "YouTube Data API v3" → Enable
4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: "Desktop app"
   - Download JSON file

## Place Credentials

1. Rename downloaded file to `client_secrets.json`
2. Place in project root:
   ```
   UploadVerse/
   ├── client_secrets.json    ← Place here
   └── .env
   ```

## Authenticate

```bash
# Using Python
python -c "from video_publisher.platforms.youtube.uploader import YouTubeUploader; u=YouTubeUploader(); u.authenticate()"

# Or using CLI (if installed)
video-publisher auth youtube
```

**What happens:**
- Browser opens for Google OAuth
- Sign in and grant permissions
- Token saved to `data/sessions/youtube_token.pickle`

## Verify

```bash
video-publisher status
# Should show: YouTube: Authenticated
```

## Upload Example

```bash
video-publisher upload video.mp4 --platforms youtube --title "My Video"
```

**File Structure:**
```
UploadVerse/
├── .env
├── client_secrets.json       ← From Google Cloud
├── data/
│   └── sessions/
│       └── youtube_token.pickle  ← Created by auth
└── your_video.mp4
```
