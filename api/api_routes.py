"""
API routes blueprint - REST API endpoints
"""
import os
import uuid
import threading
from pathlib import Path
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from video_publisher import upload_video, get_publisher, Platform

api_bp = Blueprint('api', __name__)

# In-memory storage for upload status (use Redis/DB in production)
upload_status = {}

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def background_upload(upload_id: str, video_path: str, platforms: list, metadata: dict):
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

@api_bp.route('/')
def index():
    """API information."""
    return jsonify({
        'name': 'Video Publisher API',
        'version': '0.1.0',
        'endpoints': {
            'POST /api/upload': 'Upload a video',
            'GET /api/status/<upload_id>': 'Get upload status',
            'GET /api/platforms': 'List available platforms',
            'GET /api/metrics': 'Get system metrics'
        }
    })

@api_bp.route('/upload', methods=['POST'])
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
    from flask import current_app
    filename = secure_filename(file.filename)
    upload_id = str(uuid.uuid4())
    file_path = current_app.config['UPLOAD_FOLDER'] / f"{upload_id}_{filename}"
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
        'message': 'Upload queued for processing. Use /api/status/<upload_id> to check progress.'
    }), 202

@api_bp.route('/status/<upload_id>', methods=['GET'])
def status(upload_id: str):
    """Get the status of an upload."""
    if upload_id not in upload_status:
        return jsonify({'error': 'Upload ID not found'}), 404
    
    return jsonify(upload_status[upload_id])

@api_bp.route('/platforms', methods=['GET'])
def platforms():
    """List available platforms and their authentication status."""
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

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    publisher = get_publisher()
    if publisher.emergency_stop.is_triggered():
        return jsonify({'status': 'emergency_stop_active'}), 503
    return jsonify({'status': 'healthy'}), 200

@api_bp.route('/metrics', methods=['GET'])
def metrics():
    """Get system metrics and rate limits."""
    publisher = get_publisher()
    
    metrics_data = {
        'system_status': 'emergency_stop' if publisher.emergency_stop.is_triggered() else 'operational',
        'platforms': {}
    }
    
    platforms_map = {
        "youtube": Platform.YOUTUBE,
        "tiktok": Platform.TIKTOK,
        "instagram": Platform.INSTAGRAM
    }
    
    for name, platform_enum in platforms_map.items():
        remaining = publisher.rate_limiter.get_remaining(platform_enum)
        limit = publisher.rate_limiter.limits.get(platform_enum, 5)
        used = limit - remaining
        
        metrics_data['platforms'][name] = {
            'daily_limit': limit,
            'used': used,
            'remaining': remaining,
            'authenticated': False
        }
        
        if platform_enum in publisher.uploaders:
            metrics_data['platforms'][name]['authenticated'] = publisher.uploaders[platform_enum].is_authenticated()
            
    return jsonify(metrics_data)
