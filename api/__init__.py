# Upload Manager - Shared instance
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from upload_manager import UploadManager

# Create shared instance
upload_mgr = UploadManager()
