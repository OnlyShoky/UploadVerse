## CONTEXT: Refer to Masterplan.md
Create the CORE ENGINE shared by all three interfaces.

Generate COMPLETE:
1. src/video_publisher/core/engine.py - Main VideoPublisher class
   - Methods: upload(video_path, platforms="auto")
2. src/video_publisher/core/video_analyzer.py - Video format detection
   - Detect 16:9 vs 9:16 using moviepy/opencv
3. src/video_publisher/core/platform_router.py - Smart routing
   - Horizontal → YouTube only
   - Vertical → TikTok, Instagram, YouTube Shorts
4. src/video_publisher/core/models.py - Pydantic models
5. Unit tests for all core functionality

Design for use by: Library, CLI, and Web API.