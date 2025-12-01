## CONTEXT: Refer to Masterplan.md
Implement the THREE interfaces using the shared core engine.

Generate COMPLETE:

A) Python Library Interface:
- src/video_publisher/__init__.py - Clean public API
- Usage: from video_publisher import upload_video

B) CLI Interface:
- cli/main.py with Click/Typer
- Commands: upload, auth, config, status
- Usage: video-publisher upload test.mp4 --platforms all

C) Web API Interface:
- api/app.py Flask application
- Routes: POST /upload, GET /status/:id
- Usage: curl -X POST -F "video=@test.mp4" http://localhost:5000/upload

All three must use the SAME VideoPublisher engine.