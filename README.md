# UploadVerse

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Multi-platform video publishing automation with smart format detection.**

Automatically upload videos to YouTube, TikTok, and Instagram with intelligent routing based on aspect ratio.

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/OnlyShoky/UploadVerse.git
cd UploadVerse
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Upgrade pip
python -m pip install --upgrade pip

# Install
pip install -r requirements.txt
pip install -e .

# Run app 
python .\app.py

# Authenticate YouTube
video-publisher auth youtube

# Upload
# Upload
video-publisher upload video.mp4 --platforms youtube
video-publisher upload video.mp4 --platforms tiktok --metadata metadata.json
video-publisher upload video1.mp4 video2.mp4 --platforms tiktok  # Batch upload
```

---

## 📋 Prerequisites

- Python 3.10+
- Google Cloud account (for YouTube)
- Chrome browser (for TikTok/Instagram)

---

## ⚙️ Configuration

Create `.env` file:
```bash
# YouTube (safe, recommended)
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json

# TikTok (⚠️ use test accounts only)
TIKTOK_HEADLESS=false

# Instagram (🔴 high ban risk, use test accounts only)
INSTAGRAM_HEADLESS=false
```

---

## 🔑 Platform Setup

### YouTube (Recommended)
- Uses official Google API
- Safe and reliable
- [Setup Guide →](docs/youtube_setup.md)

### TikTok
- ⚠️ Browser automation (violates TOS)
- Use test accounts only
- [Setup Guide →](docs/tiktok_setup.md)

### Instagram  
- 🔴 High ban risk (violates TOS)
- Use test accounts only
- [Setup Guide →](docs/instagram_setup.md)

---

## 💻 CLI Usage

### Basic Upload
```bash
# Upload (auto-detects platform from aspect ratio)
video-publisher upload video.mp4

# Specify platform
video-publisher upload video.mp4 --platforms youtube
video-publisher upload video.mp4 --platforms tiktok
```

### Advanced Features
```bash
# Custom Thumbnail
video-publisher upload video.mp4 --platforms tiktok --thumbnail cover.jpg

# With simple metadata
video-publisher upload video.mp4 \
  --platforms youtube \
  --title "My Video" \
  --description "Description" \
  --tags "tag1,tag2"
```

### Batch Upload & Auto-Discovery
Process multiple videos in a single browser session. Metadata files (`.json`) and thumbnails (`.jpg`/`.png`) are automatically detected if they share the same filename as the video.

**Example: 3 Videos with unique metadata & thumbnails**
Given these files:
- `vids/clip1.mp4`, `vids/clip1.json`, `vids/clip1.jpg`
- `vids/clip2.mp4`, `vids/clip2.json` (no thumb)
- `vids/clip3.mp4` (no metadata, no thumb)

Run:
```bash
video-publisher upload vids/clip1.mp4 vids/clip2.mp4 vids/clip3.mp4 --platforms tiktok

video-publisher upload video1.mp4 video2.mp4 --platforms tiktok \
  --metadata "meta1.json,meta2.json" \
  --thumbnail "thumb1.jpg,thumb2.jpg"

video-publisher upload .\data\videos\112_es_vertical.mp4 .\data\videos\112_es_vertical.mp4 --platforms tiktok --metadata ".\data\videos\112_es_horizontal.json,.\data\videos\112_es_horizontal2.json" --thumbnail ".\data\videos\thumb_114_en_1.jpg,.\data\videos\thumb_114_en_2.jpg"
```

**What happens:**
1. **clip1**: Uploads with title/tags from `clip1.json` AND custom cover `clip1.jpg`.
2. **clip2**: Uploads with title/tags from `clip2.json`.
3. **clip3**: Uploads with default settings.
*All uploads occur in ONE browser session.*

### Other Commands
```bash
# Check status
video-publisher status

# Authenticate
video-publisher auth youtube
video-publisher auth tiktok
video-publisher auth instagram
```

**[Full CLI Reference →](docs/cli_usage.md)**

---

## 📁 File Structure

```
UploadVerse/
├── .env                       ← Your config
├── client_secrets.json        ← YouTube OAuth (from Google Cloud)
├── data/
│   ├── videos/               ← Your videos
│   └── sessions/             ← Auth tokens (auto-created)
│       ├── youtube_token.pickle
│       ├── tiktok_session.pkl
│       └── instagram_session.pkl
├── docs/                     ← Documentation
│   ├── youtube_setup.md
│   ├── tiktok_setup.md
│   ├── instagram_setup.md
│   └── cli_usage.md
└── src/                      ← Source code
```

---

## 🎨 Features

- **Smart Routing**: 16:9 → YouTube, 9:16 → TikTok/Instagram
- **Multi-Platform**: Upload to multiple platforms simultaneously
- **CLI Interface**: Simple command-line tool
- **Python Library**: Programmatic access
- **Authentication**: Persistent sessions/tokens

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [YouTube Setup](docs/youtube_setup.md) | Google Cloud Console + OAuth setup |
| [TikTok Setup](docs/tiktok_setup.md) | Browser automation setup (risky) |
| [Instagram Setup](docs/instagram_setup.md) | Browser automation setup (very risky) |
| [CLI Usage](docs/cli_usage.md) | All CLI commands and examples |

---

## ⚠️ Important Warnings

### TikTok
- Automation violates TikTok Terms of Service
- Account bans are common
- **Always use test accounts**

### Instagram
- Automation violates Instagram Terms of Service
- Account bans are almost guaranteed
- **Never use your personal account**
- Very high risk

### YouTube
- ✅ Uses official API (safe)
- No TOS violations
- Recommended platform

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
pytest
```

---

## 📄 License

MIT License

---

## 🙏 Built With

- [Google API Python Client](https://github.com/googleapis/google-api-python-client) - YouTube API
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Stealth automation
- [Selenium](https://www.selenium.dev/) - Browser automation
- [MoviePy](https://zulko.github.io/moviepy/) - Video processing
- [Typer](https://typer.tiangolo.com/) - CLI framework

---

**Version:** 0.1.0  
**Status:** Alpha  
**Repository:** https://github.com/OnlyShoky/UploadVerse
