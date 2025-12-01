# YouTube Authentication & Upload Guide

## Overview

This guide explains how to authenticate with YouTube and upload videos using the Video Publisher.

---

## Prerequisites

- Google account
- Google Cloud Console access
- Python 3.10+ installed

---

## Step-by-Step Setup

### 1. Create Google Cloud Project (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name: **"Video Publisher"** (or your preferred name)
4. Click **"Create"**
5. Wait for project creation to complete

---

### 2. Enable YouTube Data API v3 (2 minutes)

1. In your project, navigate to **"APIs & Services"** → **"Library"**
2. Search for: **"YouTube Data API v3"**
3. Click on it
4. Click **"Enable"**
5. Wait for activation

---

### 3. Configure OAuth Consent Screen (3 minutes)

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type (or "Internal" if using Google Workspace)
3. Click **"Create"**
4. Fill in required fields:
   - **App name**: "Video Publisher"
   - **User support email**: Your email
   - **Developer contact**: Your email
5. Click **"Save and Continue"**
6. **Scopes**: Click "Save and Continue" (we'll add scopes in credentials)
7. **Test users**: Add your email (click "Add Users")
8. Click **"Save and Continue"**
9. Review and click **"Back to Dashboard"**

---

### 4. Create OAuth2 Credentials (5 minutes)

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Application type: **"Desktop app"**
4. Name: **"Video Publisher Desktop"**
5. Click **"Create"**
6. **IMPORTANT**: Click the **Download** button (⬇️) next to your new credential
7. Save the file

---

### 5. Place Credentials File (1 minute)

Rename the downloaded file to `client_secrets.json` and place it in your project root:

```
D:\Proyectos\Automatizations\UploadVerse\client_secrets.json
```

**Verify the file structure:**
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "YOUR_CLIENT_SECRET",
    ...
  }
}
```

---

## Authentication Process

### Option 1: Using Helper Script (Recommended)

```bash
python scripts/setup_youtube_auth.py
```

**What happens:**
1. Script checks for `client_secrets.json`
2. Opens browser for OAuth2 authorization
3. You sign in with Google
4. Grant permissions
5. Token saved to `data/sessions/youtube_token.pickle`

---

### Option 2: Manual Authentication

```bash
python -c "from video_publisher.platforms.youtube.uploader import YouTubeUploader; u=YouTubeUploader(); u.authenticate()"
```

---

## OAuth2 Authorization Flow

When you run authentication:

1. **Browser Opens**: URL like `https://accounts.google.com/o/oauth2/auth?...`

2. **Sign In**: Choose your Google account

3. **Warning Screen**: "Google hasn't verified this app"
   - This is normal for development apps
   - Click **"Advanced"**
   - Click **"Go to Video Publisher (unsafe)"**
   - This is safe because it's YOUR app

4. **Permission Request**: 
   - "Video Publisher wants to access your Google Account"
   - Shows: "Upload videos to YouTube"
   - Click **"Allow"**

5. **Success**: 
   - Browser shows: "The authentication flow has completed"
   - Close the browser
   - Token file created: `data/sessions/youtube_token.pickle`

---

## Uploading Videos

### Test Upload (Interactive)

```bash
python scripts/test_youtube_upload.py
```

This will ask you:
- Video file path
- Title
- Description
- Tags
- Privacy setting (private/unlisted/public)

---

### CLI Upload

```bash
# Basic upload
video-publisher upload video.mp4 --platforms youtube

# With metadata
video-publisher upload video.mp4 \
  --platforms youtube \
  --title "My Video Title" \
  --description "My video description" \
  --tags "tag1,tag2,tag3"
```

---

### Library Upload

```python
from video_publisher import upload_video

results = upload_video(
    'video.mp4',
    platforms=['youtube'],
    metadata={
        'title': 'My Video',
        'description': 'Description here',
        'privacy_status': 'private',  # private, unlisted, or public
        'tags': ['tag1', 'tag2'],
        'category_id': '22'  # 22 = People & Blogs
    }
)

for result in results:
    if result.success:
        print(f"✅ Uploaded: {result.url}")
    else:
        print(f"❌ Failed: {result.error}")
```

---

## Privacy Settings

**Available options:**
- `private` - Only you can see (recommended for testing)
- `unlisted` - Anyone with the link can see
- `public` - Everyone can see and search

**Default**: Public (be careful!)

**Change default** by modifying metadata:
```python
metadata = {'privacy_status': 'private'}
```

---

## Video Categories

Common category IDs:
- `1` - Film & Animation
- `10` - Music
- `17` - Sports
- `20` - Gaming
- `22` - People & Blogs (default)
- `23` - Comedy
- `24` - Entertainment
- `25` - News & Politics
- `26` - How-to & Style
- `27` - Education
- `28` - Science & Technology

Full list: https://developers.google.com/youtube/v3/docs/videoCategories

---

## Quota Limits

YouTube Data API has daily quotas:

**Free Tier:**
- 10,000 units per day (default)
- 1 video upload = ~1,600 units
- ~6 uploads per day on free tier

**Operations costs:**
- Upload video: 1,600 units
- Update video: 50 units
- List videos: 1 unit

**Check quota**: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

---

## Troubleshooting

### Error: "client_secrets.json not found"
**Solution**: Make sure the file is in the project root with exact name `client_secrets.json`

### Error: "The authentication flow has completed" but no token
**Solution**: Check `data/sessions/` directory was created. Run authentication again.

### Error: "Invalid credentials"
**Solution**: 
1. Delete `data/sessions/youtube_token.pickle`
2. Re-run authentication
3. Make sure you're using the correct Google account

### Error: "Access denied" or "Invalid grant"
**Solution**:
1. Go to Google Cloud Console
2. OAuth consent screen → Add your email to "Test users"
3. Re-authenticate

### Upload shows "video_id_placeholder"
**Solution**: 
1. Check authentication: `python tests/test_credentials.py --platform youtube --verify`
2. Check token exists: `ls data/sessions/youtube_token.pickle`
3. Re-authenticate if needed

### Error: "quota exceeded"
**Solution**: 
1. Wait 24 hours for quota reset
2. Or request quota increase in Google Cloud Console

---

## Token Management

### Token Location
```
data/sessions/youtube_token.pickle
```

### Token Lifetime
- Valid until revoked
- Refresh token automatically renews access
- No expiration unless:
  - You change credentials
  - You revoke access
  - 6 months of inactivity

### Revoke Access
1. Go to https://myaccount.google.com/permissions
2. Find "Video Publisher"
3. Click "Remove access"
4. Delete `data/sessions/youtube_token.pickle`

---

## Security Best Practices

1. **Never commit `client_secrets.json`** to Git (already in `.gitignore`)
2. **Never commit `*.pickle` files** to Git (already in `.gitignore`)
3. **Use private uploads** for testing
4. **Test with throwaway videos** first
5. **Review permissions** before clicking "Allow"
6. **Revoke access** when not in use
7. **Use service accounts** for production (future improvement)

---

## Next Steps

After successful authentication:

1. ✅ Test with a private upload
2. ✅ Verify video appears in YouTube Studio
3. ✅ Test with different metadata
4. ✅ Try unlisted/public uploads
5. ✅ Set up TikTok/Instagram (if needed)

---

## Helpful Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [YouTube Studio](https://studio.youtube.com/)
- [YouTube Data API Docs](https://developers.google.com/youtube/v3)
- [Quota Calculator](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)
- [OAuth2 Playground](https://developers.google.com/oauthplayground/)

---

## Support

For issues:
1. Check this guide
2. Run: `python tests/test_credentials.py --platform youtube --verify`
3. Check logs in terminal output
4. Review `USER_SETUP.md` for additional help
