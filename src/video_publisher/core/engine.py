from typing import List, Optional
from .models import VideoMetadata, Platform, UploadResult
from .video_analyzer import VideoAnalyzer
from .platform_router import PlatformRouter
from ..platforms.youtube.uploader import YouTubeUploader
from ..platforms.tiktok.uploader import TikTokUploader
from ..platforms.instagram.uploader import InstagramUploader
from ..safety import RateLimiter, RiskDetector, EmergencyStop

class VideoPublisher:
    def __init__(self):
        self.analyzer = VideoAnalyzer()
        self.router = PlatformRouter()
        
        # Safety Systems
        self.rate_limiter = RateLimiter()
        self.risk_detector = RiskDetector()
        self.emergency_stop = EmergencyStop()
        
        # Initialize platform uploaders
        self.uploaders = {
            Platform.YOUTUBE: YouTubeUploader(),
            Platform.YOUTUBE_SHORTS: YouTubeUploader(),  # Same uploader, different routing
            Platform.TIKTOK: TikTokUploader(),
            Platform.INSTAGRAM: InstagramUploader()
        }

    def upload(self, video_path: str, platforms: Optional[List[Platform]] = None, metadata: Optional[dict] = None) -> List[UploadResult]:
        """
        Orchestrates the video upload process.
        
        Args:
            video_path: Path to the video file.
            platforms: Optional list of platforms to upload to. If None, platforms are determined automatically.
            metadata: Optional metadata dict for the upload (title, description, etc.)
            
        Returns:
            List of UploadResult objects.
        """
        # 0. Emergency Stop Check
        if self.emergency_stop.is_triggered():
            print("🚨 EMERGENCY STOP TRIGGERED! Aborting uploads.")
            return [UploadResult(platform=p, success=False, error="Emergency Stop Triggered") 
                   for p in (platforms or [])]

        # 1. Analyze
        print(f"Analyzing video: {video_path}")
        video_metadata = self.analyzer.analyze(video_path)
        print(f"Metadata: {video_metadata}")
        
        # 2. Risk Detection
        upload_metadata = metadata or {}
        is_safe, warnings = self.risk_detector.check(upload_metadata)
        if warnings:
            print("⚠️  Risk Warnings:")
            for w in warnings:
                print(f"  - {w}")
            if not is_safe:
                print("❌ Risk check failed. Aborting upload.")
                return [UploadResult(platform=p, success=False, error=f"Risk check failed: {warnings[0]}") 
                       for p in (platforms or [])]
        
        # 3. Route
        if platforms:
            target_platforms = platforms
        else:
            target_platforms = self.router.route(video_metadata)
        
        print(f"Target platforms: {[p.value for p in target_platforms]}")
        
        # 4. Upload to each platform
        results = []
        
        for platform in target_platforms:
            print(f"Processing {platform.value}...")
            
            # Rate Limit Check
            if not self.rate_limiter.can_upload(platform):
                print(f"❌ Rate limit exceeded for {platform.value}. Skipping.")
                results.append(UploadResult(
                    platform=platform,
                    success=False,
                    error="Daily rate limit exceeded"
                ))
                continue
            
            print(f"Uploading to {platform.value}...")
            
            if platform in self.uploaders:
                uploader = self.uploaders[platform]
                result = uploader.upload(video_path, upload_metadata)
                
                if result.success:
                    self.rate_limiter.record_upload(platform)
                    remaining = self.rate_limiter.get_remaining(platform)
                    print(f"✅ Upload successful! ({remaining} uploads remaining today)")
                
                results.append(result)
            else:
                # Platform not yet implemented
                results.append(UploadResult(
                    platform=platform,
                    success=False,
                    error=f"Platform {platform.value} not yet implemented"
                ))
            
        return results
