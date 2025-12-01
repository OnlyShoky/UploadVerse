import json
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..core.models import Platform

class RateLimiter:
    """
    Enforces rate limits for uploads to prevent platform bans or quota errors.
    Persists usage data to disk to maintain limits across CLI runs.
    """
    
    # Default limits (uploads per day)
    DEFAULT_LIMITS = {
        Platform.YOUTUBE: 6,      # Conservative limit for free tier
        Platform.YOUTUBE_SHORTS: 6,
        Platform.TIKTOK: 4,       # To avoid spam detection
        Platform.INSTAGRAM: 4     # To avoid action blocks
    }
    
    def __init__(self, storage_path: str = "data/safety/rate_limits.json"):
        self.storage_path = Path(storage_path)
        self.limits = self.DEFAULT_LIMITS.copy()
        self._ensure_storage()
        self._load_usage()

    def _ensure_storage(self):
        """Ensure storage directory exists."""
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_usage(self):
        """Load usage data from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to Platform enums if needed, 
                    # but JSON keys are always strings. We'll handle conversion on access.
                    self.usage = data
            except Exception:
                self.usage = {}
        else:
            self.usage = {}

    def _save_usage(self):
        """Save usage data to disk."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.usage, f, indent=2)

    def _get_today_key(self) -> str:
        """Get date string for today."""
        return datetime.now().strftime("%Y-%m-%d")

    def can_upload(self, platform: Platform) -> bool:
        """
        Check if upload is allowed for the platform.
        
        Args:
            platform: The target platform.
            
        Returns:
            True if within limits, False otherwise.
        """
        today = self._get_today_key()
        platform_key = platform.value
        
        # Initialize if not present
        if today not in self.usage:
            self.usage[today] = {}
        
        current_count = self.usage[today].get(platform_key, 0)
        limit = self.limits.get(platform, 5) # Default fallback
        
        return current_count < limit

    def record_upload(self, platform: Platform):
        """
        Record a successful upload.
        
        Args:
            platform: The target platform.
        """
        today = self._get_today_key()
        platform_key = platform.value
        
        if today not in self.usage:
            self.usage[today] = {}
            
        current_count = self.usage[today].get(platform_key, 0)
        self.usage[today][platform_key] = current_count + 1
        self._save_usage()

    def get_remaining(self, platform: Platform) -> int:
        """Get remaining uploads for today."""
        today = self._get_today_key()
        platform_key = platform.value
        
        current_count = self.usage.get(today, {}).get(platform_key, 0)
        limit = self.limits.get(platform, 5)
        
        return max(0, limit - current_count)
