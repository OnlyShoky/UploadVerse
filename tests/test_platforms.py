import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

from video_publisher.platforms.base import BasePlatform
from video_publisher.platforms.youtube.uploader import YouTubeUploader
from video_publisher.platforms.tiktok.uploader import TikTokUploader
from video_publisher.platforms.instagram.uploader import InstagramUploader
from video_publisher.core.models import UploadResult, Platform

# --- Base Platform Tests ---
def test_base_platform_is_abstract():
    """BasePlatform cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BasePlatform()

# --- YouTube Uploader Tests ---
def test_youtube_uploader_init():
    """Test YouTubeUploader initialization."""
    uploader = YouTubeUploader({'credentials_file': 'test_creds.json'})
    assert uploader.credentials_file == 'test_creds.json'
    assert uploader.creds is None

@patch('video_publisher.platforms.youtube.uploader.os.path.exists')
@patch('video_publisher.platforms.youtube.uploader.pickle.load')
@patch('builtins.open', create=True)
def test_youtube_authenticate_with_existing_token(mock_open, mock_pickle_load, mock_exists):
    """Test YouTube authentication with existing valid token."""
    mock_exists.return_value = True
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_pickle_load.return_value = mock_creds
    
    uploader = YouTubeUploader()
    
    with patch('video_publisher.platforms.youtube.uploader.build') as mock_build:
        uploader.authenticate()
        assert uploader.creds == mock_creds
        mock_build.assert_called_once()

def test_youtube_is_authenticated():
    """Test YouTube is_authenticated method."""
    uploader = YouTubeUploader()
    assert uploader.is_authenticated() is False
    
    mock_creds = MagicMock()
    mock_creds.valid = True
    uploader.creds = mock_creds
    assert uploader.is_authenticated() is True

@patch('video_publisher.platforms.youtube.uploader.MediaFileUpload')
@patch('video_publisher.platforms.youtube.uploader.build')
def test_youtube_upload_success(mock_build, mock_media_upload):
    """Test successful YouTube video upload."""
    uploader = YouTubeUploader()
    
    # Mock credentials
    mock_creds = MagicMock()
    mock_creds.valid = True
    uploader.creds = mock_creds
    
    # Mock YouTube service
    mock_youtube = MagicMock()
    mock_build.return_value = mock_youtube
    uploader.youtube = mock_youtube
    
    # Mock upload request
    mock_request = MagicMock()
    mock_request.next_chunk.side_effect = [
        (None, {'id': 'test_video_123'})
    ]
    mock_youtube.videos().insert.return_value = mock_request
    
    result = uploader.upload('test.mp4', {'title': 'Test Video'})
    
    assert result.success is True
    assert result.platform == Platform.YOUTUBE
    assert 'test_video_123' in result.url

# --- TikTok Uploader Tests ---
def test_tiktok_uploader_init():
    """Test TikTokUploader initialization."""
    uploader = TikTokUploader({'cookies_file': 'test_cookies.pkl'})
    assert uploader.cookies_file == 'test_cookies.pkl'
    assert uploader.driver is None

def test_tiktok_human_delay():
    """Test TikTok human delay function."""
    uploader = TikTokUploader()
    import time
    start = time.time()
    uploader._human_delay(0.1, 0.2)
    elapsed = time.time() - start
    assert 0.1 <= elapsed <= 0.3  # Allow some margin

# --- Instagram Uploader Tests ---
def test_instagram_uploader_init():
    """Test InstagramUploader initialization."""
    uploader = InstagramUploader({
        'username': 'test_user',
        'password': 'test_pass'
    })
    assert uploader.username == 'test_user'
    assert uploader.password == 'test_pass'
    assert uploader.driver is None

def test_instagram_human_delay():
    """Test Instagram human delay function."""
    uploader = InstagramUploader()
    import time
    start = time.time()
    uploader._human_delay(0.1, 0.2)
    elapsed = time.time() - start
    assert 0.1 <= elapsed <= 0.3  # Allow some margin

# --- Integration Test (Mocked) ---
def test_all_platforms_implement_base():
    """Verify all platform uploaders implement BasePlatform."""
    assert issubclass(YouTubeUploader, BasePlatform)
    assert issubclass(TikTokUploader, BasePlatform)
    assert issubclass(InstagramUploader, BasePlatform)
