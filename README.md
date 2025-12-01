# Video Publisher

> **Status**: 🚧 Alpha Development Build v0.1.0  
> **Last Updated**: December 1, 2025  
> **Repository**: https://github.com/OnlyShoky/UploadVerse

A multi-interface video publishing automation system designed to detect video formats and route them to appropriate platforms (YouTube, TikTok, Instagram).

## ⚠️ CURRENT STATUS

**What Works:**
- ✅ Python package structure and imports
- ✅ Core video routing logic (16:9 → YouTube, 9:16 → TikTok/IG)
- ✅ 26/28 tests passing (93%)
- ✅ All platform uploader code implemented

**What Doesn't Work Yet:**
- ❌ No real video uploads tested
- ❌ No real authentication flows
- ❌ CLI command not verified
- ❌ Web API not tested
- ❌ Docker not tested

**📖 For detailed status**: See [PROJECT_STATUS.md](PROJECT_STATUS.md)  
**🚀 Quick start guide**: See [GETTING_STARTED_NOW.md](GETTING_STARTED_NOW.md)

---

## Features

- **Format Detection**: Automatically detects 16:9 vs 9:16 aspect ratios *(logic implemented, not tested with real videos)*
- **Multi-Platform Support**: 
  - YouTube via official API *(code complete, needs credentials)*
  - TikTok via browser automation *(code complete, needs testing)*
  - Instagram Reels via browser automation *(code complete, needs testing)*
- **Three Interfaces**:
  - **Library**: Python package for programmatic use *(works)*
  - **CLI**: Command-line interface *(code complete, not verified)*
  - **API**: Flask-based web API *(code complete, not tested)*
- **Dockerized**: Docker setup exists *(not tested)*

---

## Installation

### Using Virtual Environment (Recommended)

1.  Clone the repository:
    ```bash
    git clone https://github.com/OnlyShoky/UploadVerse.git
    cd UploadVerse
    ```

2.  Create and activate virtual environment:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    
    # Linux/Mac  
    python -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    # Core dependencies
    pip install -r requirements.txt
    
    # Development dependencies (includes pytest) - RECOMMENDED
    pip install -r requirements-dev.txt
    
    # API dependencies (optional)
    pip install -r requirements-api.txt
    ```

### Using pip install (Alternative)

```bash
pip install -e .[dev,api]
```

---

## ✅ Verified Working Commands

```bash
# Install dependencies (✅ WORKS)
pip install -r requirements-dev.txt

# Run core tests (✅ 5/5 PASSING)
pytest tests/test_core.py -v

# Run platform tests (✅ 11/11 PASSING - mocked)
pytest tests/test_platforms.py -v

# Import library (✅ WORKS)
python -c "from video_publisher import __version__; print(__version__)"

# Test routing logic (✅ WORKS)
python -c "from video_publisher.core.platform_router import PlatformRouter; from video_publisher.core.models import VideoMetadata; r=PlatformRouter(); m=VideoMetadata(path='test.mp4', duration=60, width=1920, height=1080, aspect_ratio=1.77); print([p.value for p in r.route(m)])"
```

---

## ⚠️ Not Yet Verified

```bash
# CLI (code exists, not tested)
video-publisher --help
video-publisher upload test.mp4 --platforms youtube

# Web API (code exists, not tested)
flask --app api.app run
curl -X POST -F "video=@test.mp4" http://localhost:5000/upload

# Docker (not tested)
docker-compose up --build
```

---

## Usage (Theoretical - Not Fully Tested)

### CLI

```bash
# Upload video (requires authentication setup first)
video-publisher upload test.mp4 --platforms youtube --title "My Video"

# Authenticate with a platform
video-publisher auth youtube

# Check authentication status
video-publisher status
```

### Library

```python
from video_publisher import upload_video

# Auto-detect platforms based on video format
results = upload_video('my_video.mp4')

# Specify platforms explicitly  
results = upload_video('my_video.mp4', platforms=['youtube'])

# Add metadata
results = upload_video(
    'my_video.mp4',
    platforms=['youtube'],
    metadata={'title': 'My Video', 'description': 'Video description'}
)

for result in results:
    if result.success:
        print(f"✅ {result.platform}: {result.url}")
    else:
        print(f"❌ {result.platform}: {result.error}")
```

### Web API

```bash
# Start the server
flask --app api.app run

# Upload a video
curl -X POST \
  -F "video=@test.mp4" \
  -F "platforms=youtube" \
  -F "title=My Video" \
  http://localhost:5000/upload

# Check upload status  
curl http://localhost:5000/status/<upload_id>

# List platforms
curl http://localhost:5000/platforms
```

---

## Testing

```bash
# All tests
pytest

# Specific test files
pytest tests/test_core.py -v          # ✅ 5/5 passing
pytest tests/test_platforms.py -v     # ✅ 11/11 passing (mocked)
pytest tests/test_interfaces.py -v    # ⚠️ 10/12 passing

# With coverage
pytest --cov=video_publisher
```

---

## Known Issues

1. **No Real Uploads**: Platform uploaders never tested with actual credentials
2. **Authentication**: No working OAuth2/session management yet
3. **Interface Tests**: 2 test failures in mock assertions
4. **CLI Entry Point**: `video-publisher` command not verified
5. **Docker**: Not tested with Docker Desktop
6. **Real Videos**: MoviePy analyzer not tested with actual video files

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for full details.

---

## Project Structure

```
UploadVerse/
├── src/video_publisher/     # Core library
│   ├── __init__.py          # Public API
│   ├── core/                # Core engine
│   │   ├── engine.py        # Main VideoPublisher
│   │   ├── video_analyzer.py
│   │   ├── platform_router.py
│   │   └── models.py
│   └── platforms/           # Platform uploaders
│       ├── base.py
│       ├── youtube/
│       ├── tiktok/
│       └── instagram/
├── cli/                     # CLI interface
│   └── main.py
├── api/                     # Web API
│   └── app.py
├── tests/                   # Test suite
├── requirements*.txt        # Dependencies
├── Dockerfile
└── docker-compose.yml
```

---

## Documentation

- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Detailed status audit
- [GETTING_STARTED_NOW.md](GETTING_STARTED_NOW.md) - What actually works today
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes

---

## Contributing

This is an early alpha build. If you want to contribute:

1. Run the tests: `pytest tests/ -v`
2. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for known issues
3. See what needs fixing
4. Submit a PR

---

## License

MIT

---

## Acknowledgments

Built with:
- [MoviePy](https://zulko.github.io/moviepy/) - Video processing
- [Google API Python Client](https://github.com/googleapis/google-api-python-client) - YouTube uploads
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Stealth automation
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Flask](https://flask.palletsprojects.com/) - Web API
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
