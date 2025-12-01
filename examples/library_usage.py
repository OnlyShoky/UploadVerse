"""
Example script demonstrating the Video Publisher library interface.

This shows how to use the library programmatically to upload videos.
"""
from pathlib import Path
from video_publisher import upload_video, get_publisher
from video_publisher.core.models import Platform

def main():
    print("🎥 Video Publisher - Example Usage\n")
    
    # Example 1: Auto-detect platform based on video format
    print("Example 1: Auto-detect (will route based on aspect ratio)")
    print("-" * 60)
    
    # Uncomment to test with a real video file
    # results = upload_video('data/videos/my_video.mp4')
    # for result in results:
    #     if result.success:
    #         print(f"✅ {result.platform.value}: {result.url}")
    #     else:
    #         print(f"❌ {result.platform.value}: {result.error}")
    
    print("Skipped (no video file)\n")
    
    # Example 2: Upload to specific platform
    print("Example 2: Upload to YouTube only")
    print("-" * 60)
    
    # Uncomment to test
    # results = upload_video(
    #     'data/videos/my_video.mp4',
    #     platforms=['youtube'],
    #     metadata={
    #         'title': 'My Test Video',
    #         'description': 'Uploaded via Video Publisher',
    #         'privacy_status': 'private'  # Start with private!
    #     }
    # )
    
    print("Skipped (no video file)\n")
    
    # Example 3: Get publisher instance for advanced usage
    print("Example 3: Using publisher instance directly")
    print("-" * 60)
    
    publisher = get_publisher()
    print(f"Publisher instance: {publisher}")
    print(f"Type: {type(publisher)}")
    print()
    
    # Example 4: Multiple platforms
    print("Example 4: Upload to multiple platforms")
    print("-" * 60)
    
    # Uncomment to test
    # results = upload_video(
    #     'data/videos/vertical_video.mp4',
    #     platforms=['tiktok', 'instagram', 'youtube'],  # Will upload to all three
    #     metadata={
    #         'caption': 'Check out this video!',  # For TikTok/IG
    #         'title': 'My Vertical Video',  # For YouTube
    #     }
    # )
    
    print("Skipped (no video file)\n")
    
    print("=" * 60)
    print("💡 Tips:")
    print("   1. Set up credentials first (see USER_SETUP.md)")
    print("   2. Test with python tests/test_credentials.py")
    print("   3. Start with YouTube (safest platform)")
    print("   4. Use 'private' uploads initially")
    print("   5. Check results for success/failure status")
    print("=" * 60)

if __name__ == '__main__':
    main()
