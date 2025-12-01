import re
from typing import List, Dict, Tuple
from ..core.models import VideoMetadata

class RiskDetector:
    """
    Analyzes video metadata for potential ban risks.
    Checks for banned words, excessive tagging, or other risky patterns.
    """
    
    # Words that might trigger shadowbans or demonetization
    BANNED_WORDS = [
        "hack", "crack", "warez", "nulled", "carding", 
        "free money", "pyramid scheme", "ponzi"
        # Add more specific to your niche
    ]
    
    def __init__(self):
        pass

    def check(self, metadata: dict) -> Tuple[bool, List[str]]:
        """
        Check metadata for risks.
        
        Args:
            metadata: Dictionary containing title, description, tags.
            
        Returns:
            Tuple (is_safe: bool, warnings: List[str])
        """
        warnings = []
        is_safe = True
        
        title = metadata.get('title', '').lower()
        description = metadata.get('description', '').lower()
        tags = metadata.get('tags', [])
        
        # 1. Check Banned Words
        for word in self.BANNED_WORDS:
            if word in title:
                warnings.append(f"Title contains risky word: '{word}'")
                is_safe = False
            if word in description:
                warnings.append(f"Description contains risky word: '{word}'")
                # Description risk might be a warning rather than a block
                
        # 2. Check Tag Stuffing
        if len(tags) > 30: # YouTube limit is around 500 chars, but >30 tags is spammy
            warnings.append(f"Excessive tags ({len(tags)}). Risk of spam detection.")
            is_safe = False
            
        # 3. Check Title Length
        if len(title) > 100:
            warnings.append("Title too long (>100 chars). May be truncated.")
            
        # 4. Check All Caps
        if len(title) > 10 and title.isupper():
            warnings.append("Title is ALL CAPS. High risk of spam classification.")
            
        return is_safe, warnings
