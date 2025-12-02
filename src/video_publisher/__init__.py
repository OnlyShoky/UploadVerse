"""
Video Publisher - Multi-platform video upload automation.

Public API for library usage.
"""
from typing import List, Optional, Dict
from .core.engine import VideoPublisher
from .core.models import VideoMetadata, Platform, UploadResult
from .platforms.youtube.uploader import YouTubeUploader
from .platforms.tiktok.uploader import TikTokUploader
from .platforms.instagram.uploader import InstagramUploader

__version__ = "0.1.0"

# Global instance for convenience
_publisher_instance: Optional[VideoPublisher] = None

def get_publisher() -> VideoPublisher:
    """Get or create the global VideoPublisher instance."""
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = VideoPublisher()
    return _publisher_instance

def upload_video(
    video_path: str,
    platforms: Optional[List[str]] = None,
    metadata: Optional[Dict] = None
) -> List[UploadResult]:
    """
    Upload a video to one or more platforms.
    
    Args:
        video_path: Path to the video file
        platforms: List of platform names ('youtube', 'tiktok', 'instagram').
                  If None, auto-detect based on video format.
        metadata: Optional metadata dict with keys like 'title', 'description', etc.
    
    Returns:
        List of UploadResult objects
    
    Example:
        >>> from video_publisher import upload_video
        >>> results = upload_video('my_video.mp4', platforms=['youtube'])
        >>> for result in results:
        ...     print(f"{result.platform}: {result.url}")
    """
    publisher = get_publisher()
    
    # Convert platform strings to Platform enum if provided
    platform_enums = None
    if platforms:
        platform_map = {
            'youtube': Platform.YOUTUBE,
            'tiktok': Platform.TIKTOK,
            'instagram': Platform.INSTAGRAM,
            'youtube_shorts': Platform.YOUTUBE_SHORTS
        }
        platform_enums = [platform_map[p.lower()] for p in platforms if p.lower() in platform_map]
    
    return publisher.upload(video_path, platforms=platform_enums, metadata=metadata)

def configure(config: Dict) -> None:
    """
    Configure the video publisher instance.
    
    Args:
        config: Configuration dictionary
    
    Example:
        >>> configure({'youtube': {'credentials_file': 'my_creds.json'}})
    """
    global _publisher_instance
    _publisher_instance = VideoPublisher()
    # TODO: Apply configuration to instance

# Export public API
__all__ = [
    '__version__',
    'upload_video',
    'configure',
    'get_publisher',
    'VideoPublisher',
    'VideoMetadata',
    'Platform',
    'UploadResult',
    'YouTubeUploader',
    'TikTokUploader',
    'InstagramUploader',
]
