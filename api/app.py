"""
Video Publisher Web API - Flask-based REST API for video uploads.
"""
import os
import uuid
from pathlib import Path
from typing import Dict, List
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import threading

from video_publisher import upload_video, get_publisher, Platform, UploadResult

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# In-memory storage for upload status (use Redis/DB in production)
upload_status: Dict[str, Dict] = {}

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def background_upload(upload_id: str, video_path: str, platforms: List[str], metadata: dict):
    """Background task for video upload."""
    try:
        upload_status[upload_id]['status'] = 'processing'
        
        results = upload_video(video_path, platforms=platforms, metadata=metadata)
        
        upload_status[upload_id]['status'] = 'completed'
        upload_status[upload_id]['results'] = [
            {
                'platform': r.platform.value,
                'success': r.success,
                'url': r.url,
                'error': r.error
            }
            for r in results
        ]
        
        # Clean up uploaded file
        os.remove(video_path)
        
    except Exception as e:
        upload_status[upload_id]['status'] = 'failed'
        upload_status[upload_id]['error'] = str(e)

@app.route('/')
def index():
    """API information."""
    return jsonify({
        'name': 'Video Publisher API',
        'version': '0.1.0',
        'endpoints': {
            'POST /upload': 'Upload a video',
            'GET /status/<upload_id>': 'Get upload status',
            'GET /platforms': 'List available platforms'
        }
    })

@app.route('/upload', methods=['POST'])
def upload():
    """
    Upload a video to one or more platforms.
    
    Form parameters:
        - video: Video file (required)
        - platforms: Comma-separated list of platforms or 'all' (optional)
        - title: Video title (optional)
        - description: Video description (optional)
        - tags: Comma-separated tags (optional)
    
    Returns:
        JSON with upload_id for status checking
    """
    # Check if file is present
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    upload_id = str(uuid.uuid4())
    file_path = app.config['UPLOAD_FOLDER'] / f"{upload_id}_{filename}"
    file.save(str(file_path))
    
    # Parse parameters
    platforms_param = request.form.get('platforms')
    platforms = None
    if platforms_param:
        if platforms_param.lower() == 'all':
            platforms = ['youtube', 'tiktok', 'instagram']
        else:
            platforms = [p.strip() for p in platforms_param.split(',')]
    
    metadata = {}
    if request.form.get('title'):
        metadata['title'] = request.form.get('title')
    if request.form.get('description'):
        metadata['description'] = request.form.get('description')
    if request.form.get('tags'):
        metadata['tags'] = [tag.strip() for tag in request.form.get('tags').split(',')]
    
    # Initialize upload status
    upload_status[upload_id] = {
        'upload_id': upload_id,
        'filename': filename,
        'status': 'queued',
        'platforms': platforms or 'auto',
        'metadata': metadata,
        'results': []
    }
    
    # Start background upload
    thread = threading.Thread(
        target=background_upload,
        args=(upload_id, str(file_path), platforms, metadata)
    )
    thread.start()
    
    return jsonify({
        'upload_id': upload_id,
        'status': 'queued',
        'message': 'Upload queued for processing. Use /status/<upload_id> to check progress.'
    }), 202

@app.route('/status/<upload_id>', methods=['GET'])
def status(upload_id: str):
    """
    Get the status of an upload.
    
    Args:
        upload_id: Upload ID returned from /upload
    
    Returns:
        JSON with upload status and results
    """
    if upload_id not in upload_status:
        return jsonify({'error': 'Upload ID not found'}), 404
    
    return jsonify(upload_status[upload_id])

@app.route('/platforms', methods=['GET'])
def platforms():
    """
    List available platforms and their authentication status.
    
    Returns:
        JSON with platform information
    """
    platform_list = [
        {
            'name': 'youtube',
            'display_name': 'YouTube',
            'auth_method': 'OAuth2',
            'supported_formats': ['horizontal', 'vertical (shorts)']
        },
        {
            'name': 'tiktok',
            'display_name': 'TikTok',
            'auth_method': 'Browser Session',
            'supported_formats': ['vertical']
        },
        {
            'name': 'instagram',
            'display_name': 'Instagram',
            'auth_method': 'Browser Session',
            'supported_formats': ['vertical (reels)']
        }
    ]
    
    return jsonify({'platforms': platform_list})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
