# Video Publisher

A multi-interface video publishing automation system designed to detect video formats and route them to appropriate platforms (YouTube, TikTok, Instagram).

## Features

- **Format Detection**: Automatically detects 16:9 vs 9:16 aspect ratios.
- **Multi-Platform Support**: Uploads to YouTube (via API) and TikTok/Instagram (via automation).
- **Three Interfaces**:
  - **Library**: Core functionality available as a Python package.
  - **CLI**: Command-line interface for scripting and manual uploads.
  - **API**: Flask-based web API for remote triggering.
- **Dockerized**: Easy deployment with Docker and Docker Compose.

## Installation

### Using Virtual Environment (Recommended)

1.  Clone the repository:
    ```bash
    git clone <repository_url>
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
    
    # Development dependencies (includes pytest)
    pip install -r requirements-dev.txt
    
    # API dependencies (optional)
    pip install -r requirements-api.txt
    ```

### Using pip install (Alternative)

1.  Install package in editable mode:
    ```bash
    pip install -e .[dev,api]
    ```

3.  Set up environment variables:
    ```bash
    cp .env.example .env
    # Edit .env with your credentials
    ```

### Docker

1.  Build and run the container:
    ```bash
    docker-compose up --build
    ```

## Usage

### CLI

```bash
video-publisher --help
```

### Library

```python
from video_publisher import Publisher

publisher = Publisher()
publisher.publish("path/to/video.mp4")
```

### API

Start the API server (if installed with `[api]` extra):

```bash
flask --app api.app run
```

## Project Structure

- `src/video_publisher/`: Core library logic.
- `cli/`: Command-line interface implementation.
- `api/`: Web API implementation.
- `tests/`: Automated tests.
