import pytest
from unittest.mock import MagicMock, patch
from video_publisher.core.models import VideoMetadata, Platform
from video_publisher.core.video_analyzer import VideoAnalyzer
from video_publisher.core.platform_router import PlatformRouter
from video_publisher.core.engine import VideoPublisher

# --- VideoAnalyzer Tests ---
def test_video_analyzer_analyze(tmp_path):
    # We mock VideoFileClip to avoid needing an actual video file
    with patch("video_publisher.core.video_analyzer.VideoFileClip") as mock_clip_cls:
        mock_clip = MagicMock()
        mock_clip.duration = 60.0
        mock_clip.size = (1920, 1080)
        mock_clip_cls.return_value.__enter__.return_value = mock_clip
        
        analyzer = VideoAnalyzer()
        metadata = analyzer.analyze("dummy.mp4")
        
        assert metadata.path == "dummy.mp4"
        assert metadata.duration == 60.0
        assert metadata.width == 1920
        assert metadata.height == 1080
        assert metadata.aspect_ratio == 1920 / 1080
        assert metadata.is_vertical is False

# --- PlatformRouter Tests ---
def test_platform_router_horizontal():
    router = PlatformRouter()
    metadata = VideoMetadata(path="test.mp4", duration=10, width=1920, height=1080, aspect_ratio=1.77)
    platforms = router.route(metadata)
    assert platforms == [Platform.YOUTUBE]

def test_platform_router_vertical():
    router = PlatformRouter()
    metadata = VideoMetadata(path="test.mp4", duration=10, width=1080, height=1920, aspect_ratio=0.56)
    platforms = router.route(metadata)
    assert set(platforms) == {Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE_SHORTS}

# --- VideoPublisher Tests ---
def test_video_publisher_upload_auto():
    with patch("video_publisher.core.engine.VideoAnalyzer") as mock_analyzer_cls, \
         patch("video_publisher.core.engine.PlatformRouter") as mock_router_cls:
        
        # Setup mocks
        mock_analyzer = mock_analyzer_cls.return_value
        mock_router = mock_router_cls.return_value
        
        metadata = VideoMetadata(path="test.mp4", duration=10, width=1920, height=1080, aspect_ratio=1.77)
        mock_analyzer.analyze.return_value = metadata
        mock_router.route.return_value = [Platform.YOUTUBE]
        
        publisher = VideoPublisher()
        results = publisher.upload("test.mp4")
        
        assert len(results) == 1
        assert results[0].platform == Platform.YOUTUBE
        assert results[0].success is True
        
        mock_analyzer.analyze.assert_called_once_with("test.mp4")
        mock_router.route.assert_called_once_with(metadata)

def test_video_publisher_upload_manual():
    with patch("video_publisher.core.engine.VideoAnalyzer") as mock_analyzer_cls:
        mock_analyzer = mock_analyzer_cls.return_value
        metadata = VideoMetadata(path="test.mp4", duration=10, width=1920, height=1080, aspect_ratio=1.77)
        mock_analyzer.analyze.return_value = metadata
        
        publisher = VideoPublisher()
        results = publisher.upload("test.mp4", platforms=[Platform.TIKTOK])
        
        assert len(results) == 1
        assert results[0].platform == Platform.TIKTOK
        assert results[0].success is True
