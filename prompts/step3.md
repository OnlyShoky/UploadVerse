## CONTEXT: Refer to Masterplan.md
Implement YouTube, TikTok, and Instagram uploaders.

Generate COMPLETE:

1. YouTube (Official API):
   - src/video_publisher/platforms/youtube/ - OAuth2 implementation
   - Features: resumable upload, metadata handling

2. TikTok (Web Automation):
   - src/video_publisher/platforms/tiktok/ - Stealth browser setup
   - Features: human delays, cookie persistence, CAPTCHA handling

3. Instagram (Web Automation):
   - src/video_publisher/platforms/instagram/ - Instagram-specific stealth
   - Features: Reels/Feed upload, session management

All platforms implement BasePlatform interface:
- upload(video_path, metadata) -> UploadResult
- is_authenticated() -> bool
- authenticate() -> None