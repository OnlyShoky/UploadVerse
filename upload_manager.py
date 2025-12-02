"""
Upload Manager - Handles file uploads and temporary storage
"""
import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4GB

class UploadManager:
    """Manages file uploads and temporary storage."""
    
    def __init__(self, upload_folder='uploads'):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(exist_ok=True)
        # In-memory storage (use Redis/DB in production)
        self.uploads = {}
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def save_file(self, file) -> dict:
        """
        Save uploaded file and return file info.
        
        Returns:
            dict with file_id, filename, path, size
        """
        if not file or not self.allowed_file(file.filename):
            raise ValueError("Invalid file type")
        
        # Generate unique ID
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        
        # Save file
        file_path = self.upload_folder / f"{file_id}_{filename}"
        file.save(str(file_path))
        
        # Get file info
        file_size = file_path.stat().st_size
        
        # Store metadata
        upload_info = {
            'file_id': file_id,
            'filename': filename,
            'path': str(file_path),
            'size': file_size,
            'uploaded_at': datetime.now().isoformat(),
            'metadata': {},
            'platforms': []
        }
        
        self.uploads[file_id] = upload_info
        return upload_info
    
    def get_upload(self, file_id: str) -> dict:
        """Get upload info by ID."""
        return self.uploads.get(file_id)
    
    def update_metadata(self, file_id: str, metadata: dict):
        """Update metadata for an upload."""
        if file_id in self.uploads:
            self.uploads[file_id]['metadata'] = metadata
    
    def update_platforms(self, file_id: str, platforms: list):
        """Update selected platforms for an upload."""
        if file_id in self.uploads:
            self.uploads[file_id]['platforms'] = platforms
    
    def cleanup_old_files(self, hours=24):
        """Remove files older than specified hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        to_remove = []
        
        for file_id, info in self.uploads.items():
            uploaded_at = datetime.fromisoformat(info['uploaded_at'])
            if uploaded_at < cutoff:
                # Delete file
                file_path = Path(info['path'])
                if file_path.exists():
                    file_path.unlink()
                to_remove.append(file_id)
        
        for file_id in to_remove:
            del self.uploads[file_id]
