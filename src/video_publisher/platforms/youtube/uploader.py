import os
import pickle
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from ..base import BasePlatform
from ...core.models import UploadResult, Platform

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeUploader(BasePlatform):
    """
    YouTube uploader using official Google API with OAuth2 authentication.
    """
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.credentials_file = self.config.get('credentials_file', 'client_secrets.json')
        self.token_file = self.config.get('token_file', 'data/sessions/youtube_token.pickle')
        
        # Ensure sessions directory exists
        token_path = Path(self.token_file)
        if not token_path.parent.exists():
            token_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.creds: Optional[Credentials] = None
        self.youtube = None
        
        # Load existing credentials if available
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                # Build YouTube service if credentials are valid
                if self.creds and self.creds.valid:
                    self.youtube = build('youtube', 'v3', credentials=self.creds)
                    print("✅ Loaded existing YouTube credentials")
                # Refresh if expired
                elif self.creds and self.creds.expired and self.creds.refresh_token:
                    print("Refreshing expired YouTube credentials...")
                    self.creds.refresh(Request())
                    self.youtube = build('youtube', 'v3', credentials=self.creds)
                    # Save refreshed token
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.creds, token)
                    print("✅ Refreshed YouTube credentials")
            except Exception as e:
                print(f"⚠️  Warning: Could not load token file: {e}")
                self.creds = None
                self.youtube = None
        
    def authenticate(self) -> None:
        """
        Authenticate with YouTube using OAuth2.
        Creates a token file for persistent authentication.
        """
        # Load existing credentials if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If no valid credentials, perform OAuth flow
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"YouTube credentials file not found: {self.credentials_file}. "
                        "Download from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=self.creds)
    
    def is_authenticated(self) -> bool:
        """
        Check if authenticated with YouTube.
        """
        return self.creds is not None and self.creds.valid
    
    def upload(self, video_path: str, metadata: dict) -> UploadResult:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to the video file.
            metadata: Dictionary with keys:
                - title: Video title
                - description: Video description
                - tags: List of tags
                - category_id: YouTube category ID (default: 22 for People & Blogs)
                - privacy_status: 'public', 'private', or 'unlisted' (default: 'public')
        
        Returns:
            UploadResult object.
        """
        print(f"🎬 YouTube upload starting...")
        print(f"   Authenticated: {self.is_authenticated()}")
        print(f"   YouTube client: {self.youtube is not None}")
        
        if not self.is_authenticated():
            print("   Running authentication...")
            self.authenticate()
        
        try:
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': metadata.get('title', Path(video_path).stem),
                    'description': metadata.get('description', ''),
                    'tags': metadata.get('tags', []),
                    'categoryId': metadata.get('category_id', '22')
                },
                'status': {
                    'privacyStatus': metadata.get('privacy_status', 'public')
                }
            }
            
            print(f"   Title: {body['snippet']['title']}")
            print(f"   Privacy: {body['status']['privacyStatus']}")
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=1024 * 1024,  # 1MB chunks
                resumable=True
            )
            
            print(f"   Initiating upload...")
            
            # Execute upload
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"   Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"✅ YouTube upload successful!")
            print(f"   URL: {video_url}")
            
            return UploadResult(
                platform=Platform.YOUTUBE,
                success=True,
                url=video_url
            )
            
        except HttpError as e:
            error_msg = f"HTTP error {e.resp.status}: {e.content.decode()}"
            print(f"❌ YouTube upload failed: {error_msg}")
            return UploadResult(
                platform=Platform.YOUTUBE,
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ YouTube upload failed: {error_msg}")
            import traceback
            traceback.print_exc()
            return UploadResult(
                platform=Platform.YOUTUBE,
                success=False,
                error=error_msg
            )
