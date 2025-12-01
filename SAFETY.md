# 🛡️ Safety Systems & Production Guide

The Video Publisher includes robust safety systems to protect your accounts and ensure reliable operation.

## 1. Safety Modules

### 🚦 Rate Limiter
Prevents platform bans by enforcing daily upload limits.
- **File**: `src/video_publisher/safety/rate_limiter.py`
- **Storage**: `data/safety/rate_limits.json`
- **Default Limits**:
  - YouTube: 6/day (Free tier safe limit)
  - TikTok: 4/day
  - Instagram: 4/day

**Usage:**
Automatically checked before every upload.
```python
# Check status via CLI
video-publisher status
```

### 🕵️ Risk Detector
Analyzes video metadata for ban risks before uploading.
- **File**: `src/video_publisher/safety/risk_detector.py`
- **Checks**:
  - Banned words in title/description
  - Excessive tags (>30)
  - ALL CAPS titles
  - Title length (>100 chars)

**Usage:**
Runs automatically. Warnings are printed to console. Critical risks abort the upload.

### 🚨 Emergency Stop
Global kill switch to immediately disable all uploads.
- **File**: `src/video_publisher/safety/emergency_stop.py`
- **Trigger**: Create a file named `STOP_ALL_UPLOADS` in project root.
- **Environment Variable**: `STOP_UPLOADS=true`

**Usage:**
```bash
# Stop everything
touch STOP_ALL_UPLOADS

# Resume
rm STOP_ALL_UPLOADS
```

---

## 2. Monitoring

### CLI Dashboard
View system status, authentication, and rate limit usage.
```bash
video-publisher status
```

### API Metrics
Get JSON metrics for monitoring systems (Prometheus/Grafana).
```bash
curl http://localhost:5000/metrics
```
**Response:**
```json
{
  "system_status": "operational",
  "platforms": {
    "youtube": {
      "daily_limit": 6,
      "used": 1,
      "remaining": 5,
      "authenticated": true
    }
  }
}
```

---

## 3. Production Deployment

### Docker
Production-ready Dockerfile included with Chrome/Selenium support.

```bash
# Build
docker build -t video-publisher .

# Run
docker run -p 5000:5000 -v $(pwd)/data:/app/data video-publisher
```

### Docker Compose
Orchestrate the service with persistent storage.

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Data Persistence
The `data/` directory is mounted as a volume to persist:
- `data/sessions/`: Authentication tokens
- `data/safety/`: Rate limit counters
- `data/logs/`: Application logs
