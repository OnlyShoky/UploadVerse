# Docker Usage

## Prerequisites

1. **Install Docker Desktop** for Windows:
   - Download from https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Wait for the whale icon in system tray to be steady (not animating)

2. **Verify Docker is running:**
   ```bash
   docker --version
   docker-compose --version
   ```

## Quick Start

```bash
# 1. Build and start
docker-compose up -d

# 2. View logs
docker-compose logs -f

# 3. Stop
docker-compose down
```

## First Time Setup

Before running Docker, configure the application:

```bash
# 1. Create .env file
cp .env.example .env

# 2. (Optional) Add YouTube credentials
# Place client_secrets.json in project root
# Then uncomment the volume mount in docker-compose.yml

# 3. Build and run
docker-compose up --build
```

## Accessing the Application

Once running:
- Web interface: http://localhost:5000
- Health check: http://localhost:5000/health

## Authentication Inside Docker

**Option 1: Outside Docker (Recommended)**
```bash
# Authenticate on your host machine first
python -c "from video_publisher.platforms.youtube.uploader import YouTubeUploader; u=YouTubeUploader(); u.authenticate()"

# The token is saved to data/sessions/ which is mounted in Docker
# Then start Docker
docker-compose up -d
```

**Option 2: Inside Docker**
```bash
# Access container shell
docker exec -it video-publisher bash

# Run authentication (won't open browser - manual token needed)
python -c "from video_publisher.platforms.youtube.uploader import YouTubeUploader; u=YouTubeUploader(); u.authenticate()"
```

**Note:** TikTok/Instagram authentication requires browser access, so authenticate on host machine first.

## Common Commands

```bash
# Build image
docker-compose build

# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Access container shell
docker exec -it video-publisher bash

# Check container status
docker ps
```

## Troubleshooting

### "Docker Desktop is not running"

**Problem:** 
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

**Solution:**
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon steady in system tray)
3. Try again

### "Cannot connect to Docker daemon"

**Solution:**
- Restart Docker Desktop
- Check Windows Services → Docker Desktop Service is running

### "client_secrets.json not found"

**Solution:**
Either:
1. Add client_secrets.json to project root
2. Or comment out the volume mount line in docker-compose.yml

### Videos uploaded but can't find them

**Solution:**
Check the mounted `data/` directory on your host machine.

## Environment Variables

Set in `.env` file or docker-compose.yml environment section:

```yaml
environment:
  - TEST_MODE=false
  - DRY_RUN=false
  - DEFAULT_PRIVACY=private
  - LOG_LEVEL=INFO
```

## Data Persistence

The `data/` directory is mounted as a volume:
- `data/sessions/` - Authentication tokens
- `data/videos/` - Uploaded videos (if saved)
- `data/logs/` - Application logs

This data persists even when container is removed.

## Production Deployment

For production use:

1. **Use environment variables for secrets**
2. **Don't commit .env or client_secrets.json to Git**
3. **Set up reverse proxy (nginx)**
4. **Use production WSGI server** (already configured: `flask run --host=0.0.0.0`)

## Rebuilding

After code changes:

```bash
# Rebuild and restart
docker-compose up --build -d

# Or rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```
