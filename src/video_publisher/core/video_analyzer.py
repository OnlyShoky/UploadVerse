from moviepy import VideoFileClip
from .models import VideoMetadata

class VideoAnalyzer:
    def analyze(self, video_path: str) -> VideoMetadata:
        """
        Analyzes the video file to extract metadata.
        """
        try:
            with VideoFileClip(video_path) as clip:
                return VideoMetadata(
                    path=video_path,
                    duration=clip.duration,
                    width=clip.size[0],
                    height=clip.size[1],
                    aspect_ratio=clip.size[0] / clip.size[1]
                )
        except Exception as e:
            raise ValueError(f"Failed to analyze video at {video_path}: {str(e)}")
