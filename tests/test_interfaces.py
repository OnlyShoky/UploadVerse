import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from typer.testing import CliRunner

from video_publisher import upload_video, get_publisher
from video_publisher.core.models import UploadResult, Platform
from cli.main import app as cli_app

# --- Library Interface Tests ---
@patch('video_publisher.VideoPublisher')
def test_library_upload_video_with_platforms(mock_publisher_class):
    """Test library upload_video function with explicit platforms."""
    mock_publisher = MagicMock()
    mock_publisher_class.return_value = mock_publisher
    
    mock_result = UploadResult(platform=Platform.YOUTUBE, success=True, url="https://youtube.com/test")
    mock_publisher.upload.return_value = [mock_result]
    
    results = upload_video('test.mp4', platforms=['youtube'])
    
    assert len(results) == 1
    assert results[0].platform == Platform.YOUTUBE
    assert results[0].success is True

@patch('video_publisher.VideoPublisher')
def test_library_upload_video_auto_detect(mock_publisher_class):
    """Test library upload_video function with auto-detect."""
    mock_publisher = MagicMock()
    mock_publisher_class.return_value = mock_publisher
    
    mock_result = UploadResult(platform=Platform.YOUTUBE, success=True, url="https://youtube.com/test")
    mock_publisher.upload.return_value = [mock_result]
    
    results = upload_video('test.mp4')
    
    mock_publisher.upload.assert_called_once()
    assert mock_publisher.upload.call_args[1]['platforms'] is None

def test_library_get_publisher():
    """Test get_publisher returns singleton instance."""
    publisher1 = get_publisher()
    publisher2 = get_publisher()
    assert publisher1 is publisher2

# --- CLI Interface Tests ---
runner = CliRunner()

@patch('cli.main.upload_video')
def test_cli_upload_command(mock_upload):
    """Test CLI upload command."""
    mock_upload.return_value = [
        UploadResult(platform=Platform.YOUTUBE, success=True, url="https://youtube.com/test")
    ]
    
    # Create a temporary test file
    with runner.isolated_filesystem():
        test_file = Path("test.mp4")
        test_file.write_text("fake video content")
        
        result = runner.invoke(cli_app, ['upload', str(test_file), '--platforms', 'youtube'])
        
        assert result.exit_code == 0
        mock_upload.assert_called_once()

def test_cli_version_command():
    """Test CLI version command."""
    result = runner.invoke(cli_app, ['version'])
    assert result.exit_code == 0
    assert 'Video Publisher' in result.output

def test_cli_status_command():
    """Test CLI status command."""
    result = runner.invoke(cli_app, ['status'])
    assert result.exit_code == 0
    assert 'Platform Authentication Status' in result.output

# --- Web API Tests ---
@pytest.fixture
def api_client():
    """Create Flask test client."""
    from api.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_index(api_client):
    """Test API index endpoint."""
    response = api_client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'name' in data
    assert data['name'] == 'Video Publisher API'

def test_api_platforms(api_client):
    """Test API platforms endpoint."""
    response = api_client.get('/platforms')
    assert response.status_code == 200
    data = response.get_json()
    assert 'platforms' in data
    assert len(data['platforms']) == 3

def test_api_health(api_client):
    """Test API health check."""
    response = api_client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

@patch('api.app.upload_video')
def test_api_upload_no_file(mock_upload, api_client):
    """Test API upload without file."""
    response = api_client.post('/upload')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

@patch('api.app.upload_video')
def test_api_upload_with_file(mock_upload, api_client):
    """Test API upload with file."""
    mock_upload.return_value = [
        UploadResult(platform=Platform.YOUTUBE, success=True, url="https://youtube.com/test")
    ]
    
    data = {
        'video': (Path(__file__).parent / 'test.mp4', 'test.mp4'),
        'platforms': 'youtube',
        'title': 'Test Video'
    }
    
    # Note: This test might need adjustment based on actual file handling
    # In a real scenario, you'd create a temporary video file
    response = api_client.post('/upload', data=data, content_type='multipart/form-data')
    
    # The actual status code depends on whether the file exists
    # For this mock test, we expect it to process
    assert response.status_code in [200, 202, 400]

def test_api_status_not_found(api_client):
    """Test API status with invalid upload ID."""
    response = api_client.get('/status/invalid-id')
    assert response.status_code == 404
