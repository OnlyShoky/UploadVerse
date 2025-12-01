from typing import List, Optional
from .models import VideoMetadata, Platform, UploadResult
from .video_analyzer import VideoAnalyzer
from .platform_router import PlatformRouter

class VideoPublisher:
    def __init__(self):
        self.analyzer = VideoAnalyzer()
        self.router = PlatformRouter()

    def upload(self, video_path: str, platforms: Optional[List[Platform]] = None) -> List[UploadResult]:
        """
        Orchestrates the video upload process.
        
        Args:
            video_path: Path to the video file.
            platforms: Optional list of platforms to upload to. If None, platforms are determined automatically.
            
        Returns:
            List of UploadResult objects.
        """
        # 1. Analyze
        print(f"Analyzing video: {video_path}")
        metadata = self.analyzer.analyze(video_path)
        print(f"Metadata: {metadata}")
        
        # 2. Route
        if platforms:
            target_platforms = platforms
        else:
            target_platforms = self.router.route(metadata)
        
        print(f"Target platforms: {[p.value for p in target_platforms]}")
        
        # 3. Upload (Placeholder)
        results = []
        for platform in target_platforms:
            print(f"Uploading to {platform.value}...")
            # TODO: Implement actual upload logic for each platform
            # For now, we simulate a successful upload
            results.append(UploadResult(platform=platform, success=True, url=f"https://{platform.value}.com/video_id_placeholder"))
            
        return results
