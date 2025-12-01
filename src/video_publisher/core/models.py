from enum import Enum
from typing import Optional
from pydantic import BaseModel

class Platform(str, Enum):
    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"

class VideoMetadata(BaseModel):
    path: str
    duration: float
    width: int
    height: int
    aspect_ratio: float
    
    @property
    def is_vertical(self) -> bool:
        return self.height > self.width

class UploadResult(BaseModel):
    platform: Platform
    success: bool
    url: Optional[str] = None
    error: Optional[str] = None
