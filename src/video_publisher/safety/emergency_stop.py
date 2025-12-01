import os
from pathlib import Path

class EmergencyStop:
    """
    Global kill switch to immediately stop all automation.
    Useful if the bot goes haywire or platforms change detection methods.
    """
    
    def __init__(self, stop_file: str = "STOP_ALL_UPLOADS"):
        self.stop_file = Path(stop_file)

    def is_triggered(self) -> bool:
        """
        Check if the emergency stop is triggered.
        
        Returns:
            True if stop file exists or env var STOP_UPLOADS is set.
        """
        # Check for file existence
        if self.stop_file.exists():
            return True
            
        # Check environment variable
        if os.environ.get("STOP_UPLOADS", "").lower() == "true":
            return True
            
        return False

    def trigger(self):
        """Trigger the emergency stop manually."""
        self.stop_file.touch()

    def reset(self):
        """Reset the emergency stop."""
        if self.stop_file.exists():
            self.stop_file.unlink()
