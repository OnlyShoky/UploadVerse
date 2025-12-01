from abc import ABC, abstractmethod
from typing import Optional
from ..core.models import UploadResult

class BasePlatform(ABC):
    """
    Abstract base class for all platform uploaders.
    Each platform must implement authentication and upload logic.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the platform with optional configuration.
        
        Args:
            config: Platform-specific configuration (credentials, settings, etc.)
        """
        self.config = config or {}
    
    @abstractmethod
    def authenticate(self) -> None:
        """
        Authenticate with the platform.
        Should raise an exception if authentication fails.
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with the platform.
        
        Returns:
            True if authenticated, False otherwise.
        """
        pass
    
    @abstractmethod
    def upload(self, video_path: str, metadata: dict) -> UploadResult:
        """
        Upload a video to the platform.
        
        Args:
            video_path: Path to the video file to upload.
            metadata: Platform-specific metadata (title, description, tags, etc.)
            
        Returns:
            UploadResult object with upload status and URL.
        """
        pass
