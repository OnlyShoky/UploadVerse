from typing import List
from .models import Platform, VideoMetadata

class PlatformRouter:
    def route(self, metadata: VideoMetadata) -> List[Platform]:
        """
        Determines the target platforms based on video metadata.
        """
        if metadata.is_vertical:
            # Vertical videos go to TikTok, Instagram, and YouTube Shorts
            return [Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE_SHORTS]
        else:
            # Horizontal videos go to YouTube
            return [Platform.YOUTUBE]
