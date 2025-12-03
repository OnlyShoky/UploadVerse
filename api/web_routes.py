"""
Web routes blueprint - Frontend web interface
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from upload_manager import UploadManager
from video_publisher import get_publisher
from video_publisher.core.models import Platform

web_bp = Blueprint('web', __name__)
upload_mgr = UploadManager()

@web_bp.route('/')
def index():
    """Landing page with upload zone."""
    return render_template('index.html')

@web_bp.route('/upload', methods=['POST'])
def upload():
    """Handle file upload."""
    if 'video' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        upload_info = upload_mgr.save_file(file)
        
        # Analyze video
        from video_publisher.core.video_analyzer import VideoAnalyzer
        analyzer = VideoAnalyzer()
        video_meta = analyzer.analyze(upload_info['path'])
        
        # Store video metadata
        upload_info['video_meta'] = {
            'duration': video_meta.duration,
            'width': video_meta.width,
            'height': video_meta.height,
            'aspect_ratio': video_meta.aspect_ratio,
            'format': '16:9' if video_meta.aspect_ratio > 1 else '9:16'
        }
        
        # Redirect to config page
        return redirect(url_for('web.config', file_id=upload_info['file_id']))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/config/<file_id>')
def config(file_id):
    """Configuration page for uploaded video."""
    upload_info = upload_mgr.get_upload(file_id)
    
    if not upload_info:
        return redirect(url_for('web.index'))
    
    # Get publisher for credentials status
    publisher = get_publisher()
    
    # Check authentication status for each platform
    auth_status = {}
    for platform in [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM]:
        if platform in publisher.uploaders:
            auth_status[platform.value] = publisher.uploaders[platform].is_authenticated()
        else:
            auth_status[platform.value] = False
    
    return render_template('config.html', 
                         upload=upload_info, 
                         auth_status=auth_status)

@web_bp.route('/config/<file_id>', methods=['POST'])
def save_config(file_id):
    """Save configuration for video."""
    upload_info = upload_mgr.get_upload(file_id)
    
    if not upload_info:
        return jsonify({'error': 'Upload not found'}), 404
    
    # Get form data
    platforms = request.form.getlist('platforms')
    
    # Get schedule info
    is_scheduled = request.form.get('is_scheduled') == 'on'  # Checkboxes return 'on' when checked
    schedule_time = request.form.get('schedule_time')
    
    metadata = {
        'title': request.form.get('title', ''),
        'description': request.form.get('description', ''),
        'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
        'privacy_status': request.form.get('privacy', 'public'),
        'category_id': request.form.get('category', '22'),
        'category_id': request.form.get('category', '22'),
        'scheduling': {
            'publish_now': not is_scheduled,
            'scheduled_time': schedule_time if is_scheduled else None
        }
    }

    
    # Update upload info
    upload_mgr.update_platforms(file_id, platforms)
    upload_mgr.update_metadata(file_id, metadata)
    
    # Redirect to review page
    return redirect(url_for('web.review', file_id=file_id))

@web_bp.route('/review/<file_id>')
def review(file_id):
    """Review and publish page."""
    upload_info = upload_mgr.get_upload(file_id)
    
    if not upload_info:
        return redirect(url_for('web.index'))
    
    return render_template('publish.html', upload=upload_info)

@web_bp.route('/publish/<file_id>', methods=['POST'])
def publish(file_id):
    """Start publish process."""
    upload_info = upload_mgr.get_upload(file_id)
    
    if not upload_info:
        return jsonify({'error': 'Upload not found'}), 404
    
    # Import video_publisher
    from video_publisher import upload_video
    
    # Start upload
    platforms = upload_info.get('platforms', [])
    metadata = upload_info.get('metadata', {})
    
    try:
        results = upload_video(
            upload_info['path'],
            platforms=platforms,
            metadata=metadata
        )
        
        # Format results
        result_data = [
            {
                'platform': r.platform.value,
                'success': r.success,
                'url': r.url,
                'error': r.error
            }
            for r in results
        ]
        
        return jsonify({
            'status': 'success',
            'results': result_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# HTMX Partials
@web_bp.route('/partials/platform/<platform_name>')
def platform_form(platform_name):
    """Return platform-specific form HTML."""
    return render_template(f'components/platform_form_{platform_name}.html')

@web_bp.route('/partials/credentials-status')
def credentials_status():
    """Return credentials status HTML (for HTMX polling)."""
    publisher = get_publisher()
    
    auth_status = {}
    rate_limits = {}
    
    for platform in [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM]:
        platform_key = platform.value
        
        # Auth status
        if platform in publisher.uploaders:
            auth_status[platform_key] = publisher.uploaders[platform].is_authenticated()
        else:
            auth_status[platform_key] = False
        
        # Rate limits
        remaining = publisher.rate_limiter.get_remaining(platform)
        limit = publisher.rate_limiter.limits.get(platform, 5)
        rate_limits[platform_key] = {
            'remaining': remaining,
            'limit': limit
        }
    
    return render_template('components/credentials_status.html',
                         auth_status=auth_status,
                         rate_limits=rate_limits)

@web_bp.route('/auth/<platform>')
def auth_platform(platform):
    """Initiate authentication for a platform."""
    from video_publisher.platforms.youtube.uploader import YouTubeUploader
    
    if platform == 'youtube':
        uploader = YouTubeUploader()
        # Use web-based auth flow
        redirect_uri = url_for('web.oauth2callback', _external=True)
        auth_url = uploader.get_auth_url(redirect_uri)
        return redirect(auth_url)
    else:
        return jsonify({'error': f'Authentication for {platform} not yet implemented'}), 501

@web_bp.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth2 callback."""
    from video_publisher.platforms.youtube.uploader import YouTubeUploader
    
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
        
    try:
        uploader = YouTubeUploader()
        redirect_uri = url_for('web.oauth2callback', _external=True)
        uploader.finish_auth(code, redirect_uri)
        return redirect(url_for('web.index'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve uploaded videos
from flask import send_from_directory

@web_bp.route('/videos/<path:filename>')
def serve_video(filename):
    """Serve uploaded video files."""
    import os
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    return send_from_directory(uploads_dir, filename)

