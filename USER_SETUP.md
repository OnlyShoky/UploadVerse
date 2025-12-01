# User Setup Guide - Video Publisher

**Last Updated**: December 1, 2025  
**Purpose**: What YOU need to provide to make the project work

> ⚠️ **IMPORTANT**: This guide tells you what resources and credentials you must provide from your side. The code is ready, but it needs YOUR inputs to function.

---

## 🎯 Quick Start (Minimum Setup)

**To test the project without any uploads:**
- ✅ Nothing needed! Tests run with mocks
- ✅ Library imports and routing logic work out of the box

**To make ONE real YouTube upload:**
- 📝 Google Cloud Console project + OAuth2 credentials (30 min setup)
- 🎥 One test video file
- ⏱️ About 1 hour total

**For TikTok/Instagram:**
- ⚠️ Requires browser automation + test accounts
- ⚠️ Higher risk - use burner accounts only
- ⏱️ Additional 2-3 hours setup + testing

---

## 📋 WHAT YOU NEED TO PROVIDE

### 1. Platform Credentials

#### ▶️ YouTube (RECOMMENDED TO START)

**What You Need:**
- Google Cloud Console project
- OAuth 2.0 Client ID and Client Secret
- Downloaded `client_secrets.json` file

**How to Get It:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable "YouTube Data API v3"
   - Navigation: APIs & Services → Library → Search "YouTube Data API v3" → Enable
4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: "Desktop app"
   - Download JSON file as `client_secrets.json`

**Where to Put It:**
```
UploadVerse/
├── client_secrets.json    # ← Put the downloaded file here (at project root)
└── .env                   # Will be created automatically after first auth
```

**Cost:** ✅ FREE (YouTube API quota: 10,000 units/day, sufficient for dozens of uploads)

**Safety:** ✅ SAFE - Official Google API, just use "private" uploads initially

---

#### 🎵 TikTok (RISKIER - Use Test Account)

**What You Need:**
- Personal TikTok account credentials (username + password)
- OR session cookies from a logged-in browser

**How to Get It:**
- Option A: Use existing personal account (⚠️ RISKY)
- Option B: Create a NEW test/burner account (✅ RECOMMENDED)

**Where to Put It:**
```
.env file:
TIKTOK_USERNAME=your_username
TIKTOK_PASSWORD=your_password
```

**Cost:** ✅ FREE (no API needed, uses web automation)

**Safety:** ⚠️ RISKY
- TikTok may detect automation and ban account
- Use test account you don't care about
- Start with `DRY_RUN=true` mode

**Alternative:** Don't use TikTok initially, focus on YouTube first

---

#### 📷 Instagram (RISKIEST - Use Test Account)

**What You Need:**
- Personal Instagram account credentials
- NO Facebook Developer setup needed (uses web automation)

**How to Get It:**
- Create a NEW Instagram account specifically for testing
- Don't use your main account

**Where to Put It:**
```
.env file:
INSTAGRAM_USERNAME=your_test_username
INSTAGRAM_PASSWORD=your_test_password
```

**Cost:** ✅ FREE (no API needed)

**Safety:** 🔴 VERY RISKY
- Instagram actively fights automation
- High chance of account ban/challenge
- NEVER use your personal account
- Expect CAPTCHAs and 2FA prompts

**Recommendation:** Skip Instagram initially, add later after YouTube works

---

### 2. Video Files

**What You Need:**
- At least one test video file to upload
- Recommended: 3-5 test videos of different formats

**Format Requirements:**
```
Supported: .mp4, .mov, .avi, .mkv, .webm
Recommended: .mp4 with H.264 codec
Size: < 500MB (configurable)
Duration: 10 seconds to 15 minutes for testing
Resolution: 720p or 1080p

Test Videos:
- 1 horizontal video (16:9) - 1920x1080
- 1 vertical video (9:16) - 1080x1920
- 1 square video (1:1) - 1080x1080 (optional)
```

**Where to Get Test Videos:**
- Create your own short test clips
- Use free stock videos: [Pexels](https://www.pexels.com/videos/) or [Pixabay](https://pixabay.com/videos/)
- Use your phone camera (quickest option)

**Where to Put Them:**
```
UploadVerse/
├── data/                     # ← Create this directory
│   └── videos/              # ← Put your test videos here
│       ├── test_horizontal.mp4
│       ├── test_vertical.mp4
│       └── my_video.mp4
└── tests/
    └── fixtures/            # ← Small dummy videos for automated tests
        └── dummy_10s.mp4    # Optional: 10-second dummy clip
```

**Create directories:**
```bash
mkdir -p data/videos
mkdir -p data/cookies
mkdir -p tests/fixtures
```

---

### 3. Configuration Files

#### Create `.env` File

**Copy from template:**
```bash
cp .env.example .env
```

**Then edit `.env` with your actual values:**

```bash
# ============================================
# YouTube Configuration (START HERE)
# ============================================
# Leave empty initially - will be filled after first OAuth flow
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_TOKEN_FILE=youtube_token.pickle

# ============================================
# TikTok Configuration (OPTIONAL - Skip initially)
# ============================================
TIKTOK_USERNAME=
TIKTOK_PASSWORD=
TIKTOK_COOKIES_FILE=data/cookies/tiktok_cookies.pkl
TIKTOK_HEADLESS=false   # Set to true after testing

# ============================================
# Instagram Configuration (OPTIONAL - Skip initially)
# ============================================
INSTAGRAM_USERNAME=
INSTAGRAM_PASSWORD=
INSTAGRAM_COOKIES_FILE=data/cookies/instagram_cookies.pkl
INSTAGRAM_HEADLESS=false

# ============================================
# Safety Settings (IMPORTANT!)
# ============================================
# Start with these enabled!
TEST_MODE=true          # Prevents actual uploads
DRY_RUN=true            # Simulates upload without executing
LOG_LEVEL=INFO          # Change to DEBUG for troubleshooting

# ============================================
# Upload Settings
# ============================================
# YouTube defaults
DEFAULT_PRIVACY=private        # Options: private, unlisted, public
DEFAULT_CATEGORY_ID=22         # 22 = People & Blogs

# Rate limiting (safety)
MAX_UPLOADS_PER_HOUR=5
RETRY_ATTEMPTS=3
```

**Which settings to fill immediately:**
1. YouTube: Just place `client_secrets.json` file, rest auto-fills
2. Safety: Keep `TEST_MODE=true` and `DRY_RUN=true` initially
3. TikTok/Instagram: Leave empty unless testing those platforms

---

## ✅ SETUP CHECKLIST

### Phase 1: Basic Setup (Required - 15 minutes)

```
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies: pip install -r requirements-dev.txt
- [ ] Run tests to verify: pytest tests/test_core.py
```

### Phase 2: YouTube Setup (Recommended - 30 minutes)

```
- [ ] Create Google Cloud project
- [ ] Enable YouTube Data API v3
- [ ] Create OAuth 2.0 credentials
- [ ] Download client_secrets.json
- [ ] Place client_secrets.json in project root
- [ ] Copy .env.example to .env
- [ ] Keep DEFAULT_PRIVACY=private in .env
```

### Phase 3: Video Preparation (Quick - 5 minutes)

```
- [ ] Create data/videos/ directory
- [ ] Add at least one test video
- [ ] Verify video plays on your computer
```

### Phase 4: First Upload Test (30 minutes)

```
- [ ] Ensure TEST_MODE=false in .env (to allow real upload)
- [ ] Ensure DEFAULT_PRIVACY=private (safety)
- [ ] Run authentication: python -c "from video_publisher.platforms.youtube.uploader import YouTubeUploader; u=YouTubeUploader(); u.authenticate()"
- [ ] Browser opens for Google OAuth (login and authorize)
- [ ] youtube_token.pickle created automatically
- [ ] Ready to upload!
```

### Phase 5: TikTok/Instagram (OPTIONAL and RISKY - Skip initially)

```
- [ ] Create burner/test account (NEVER use personal account)
- [ ] Add credentials to .env
- [ ] Test with DRY_RUN=true first
- [ ] Expect CAPTCHAs/challenges
- [ ] Be prepared for account bans
```

---

## ⚠️ CRITICAL SAFETY WARNINGS

### 🔴 DO NOT:
- ❌ Commit `.env` file to Git (already in `.gitignore`)
- ❌ Share your `client_secrets.json` publicly
- ❌ Use your personal TikTok/Instagram for testing
- ❌ Start with `public` uploads on YouTube
- ❌ Disable rate limiting initially
- ❌ Skip test mode and upload directly to production accounts

### ✅ DO:
- ✅ Start with YouTube only (safest)
- ✅ Use `private` or `unlisted` uploads initially
- ✅ Create test/burner accounts for TikTok/Instagram
- ✅ Test with `DRY_RUN=true` first
- ✅ Check uploaded videos manually on each platform
- ✅ Read platform Terms of Service
- ✅ Understand automation risks

### 🚨 Platform Risks:

**YouTube:**
- Risk: LOW ✅
- Uses official API
- Respected by Google
- Worst case: API quota exceeded (just wait a day)

**TikTok:**
- Risk: MEDIUM-HIGH ⚠️
- Web automation violates TOS
- Account bans are common
- Use test account only

**Instagram:**
- Risk: HIGH 🔴
- Very aggressive bot detection
- Account bans likely
- Requires manual intervention (CAPTCHAs, 2FA)
- NOT recommended for production use

---

## 🧪 WHAT WORKS WITHOUT YOUR INPUT

**Works immediately (no credentials needed):**
```python
# ✅ Video format detection
from video_publisher.core.video_analyzer import VideoAnalyzer
from video_publisher.core.models import VideoMetadata

# ✅ Platform routing logic
from video_publisher.core.platform_router import PlatformRouter
metadata = VideoMetadata(path="test.mp4", duration=60, width=1920, height=1080, aspect_ratio=1.77)
platforms = router.route(metadata)  # Returns [Platform.YOUTUBE]

# ✅ All unit tests (mocked)
pytest tests/
```

**Requires credentials:**
```python
# ❌ Actual YouTube upload - needs client_secrets.json
# ❌ TikTok automation - needs account credentials
# ❌ Instagram automation - needs account credentials
```

**Safe mode (simulates uploads):**
```bash
# Set in .env:
TEST_MODE=true
DRY_RUN=true

# Then run:
python your_upload_script.py
# Will show what WOULD happen without actually uploading
```

---

## 🔍 VERIFICATION COMMANDS

### Check Installation
```bash
# Dependencies installed
pip list | grep -E "google-api|selenium|moviepy|flask|typer"

# Package imports
python -c "from video_publisher import __version__; print(f'Version: {__version__}')"
```

### Check Credentials
```bash
# YouTube credentials
python -c "import os; print('client_secrets.json:', '✅' if os.path.exists('client_secrets.json') else '❌ MISSING')"

# Environment variables loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('TEST_MODE:', os.getenv('TEST_MODE', 'not set'))"
```

### Check Video Files
```bash
# Windows
dir data\videos\*.mp4

# Linux/Mac
ls -lh data/videos/*.mp4
```

### Check YouTube Auth
```bash
# After first authentication
python -c "import os; print('YouTube token:', '✅' if os.path.exists('youtube_token.pickle') else '❌ Not authenticated yet')"
```

---

## 📁 COMPLETE FILE STRUCTURE

```
UploadVerse/
├── .env                          # ← YOUR credentials (gitignored)
├── .env.example                  # Template (committed)
├── client_secrets.json           # ← YOUR YouTube OAuth file (gitignored)
├── youtube_token.pickle          # Created after first auth (gitignored)
│
├── data/                         # ← CREATE THIS
│   ├── videos/                  # ← YOUR test videos go here
│   │   ├── test_horizontal.mp4
│   │   └── test_vertical.mp4
│   ├── cookies/                 # Browser sessions (gitignored)
│   │   ├── tiktok_cookies.pkl
│   │   └── instagram_cookies.pkl
│   └── uploads/                 # Processed/uploaded videos
│
├── tests/
│   └── fixtures/                # Optional: tiny test videos
│       └── dummy.mp4
│
├── src/video_publisher/         # Code (already exists)
├── cli/                          # Code (already exists)
├── api/                          # Code (already exists)
└── prompts/                      # Documentation (already exists)
```

**What YOU create:**
- `data/` directory and subdirectories
- `.env` file (copy from `.env.example`)
- `client_secrets.json` (download from Google Cloud)
- Place your test videos in `data/videos/`

---

## 🚀 RECOMMENDED FIRST RUN

### Step 1: YouTube Only (Safest Path)

```bash
# 1. Setup
cp .env.example .env
mkdir -p data/videos
# Place client_secrets.json in project root
# Add a test video to data/videos/

# 2. Edit .env
# Set: TEST_MODE=false  (to allow real uploads)
# Set: DEFAULT_PRIVACY=private  (for safety)

# 3. Authenticate with YouTube
python -c "from video_publisher.platforms.youtube.uploader import YouTubeUploader; u=YouTubeUploader(); u.authenticate()"
# Browser opens → Login → Authorize → youtube_token.pickle created

# 4. Test upload (using library interface)
python << EOF
from video_publisher import upload_video

results = upload_video(
    'data/videos/test.mp4',
    platforms=['youtube'],
    metadata={
        'title': 'Test Upload - DELETE ME',
        'description': 'Testing Video Publisher',
        'privacy_status': 'private'
    }
)

for result in results:
    if result.success:
        print(f"✅ Uploaded: {result.url}")
    else:
        print(f"❌ Failed: {result.error}")
EOF

# 5. Check YouTube Studio
# Go to https://studio.youtube.com/ → Content → Find your private video
```

### Step 2: After YouTube Works

```bash
# Option A: Try CLI
pip install -e .
video-publisher upload data/videos/test.mp4 --platforms youtube

# Option B: Try Web API
flask --app api.app run
# In another terminal:
curl -X POST -F "video=@data/videos/test.mp4" -F "platforms=youtube" http://localhost:5000/upload
```

### Step 3: Only If Brave - TikTok/Instagram

⚠️ Not recommended initially. Wait until YouTube is solid.

---

## ❓ FAQ

**Q: Do I need to pay for anything?**  
A: No! YouTube API is free (10k units/day quota). TikTok/Instagram also free but use web automation (risky).

**Q: Can I test without uploading anything?**  
A: Yes! Set `DRY_RUN=true` in `.env` and it will simulate uploads.

**Q: What if I don't have Google Cloud Console experience?**  
A: Follow the YouTube setup guide step-by-step. It's straightforward and takes ~30 mins.

**Q: Should I use my personal TikTok/Instagram?**  
A: NO! Create test accounts. Automation violates TOS and will likely get banned.

**Q: How do I know if my setup is correct?**  
A: Run the verification commands in this  guide. All should show ✅.

**Q: What's the absolute minimum to get started?**  
A: Just `pip install -r requirements-dev.txt` and run tests. To actually upload: YouTube credentials + one video file.

---

## 🎓 LEARNING PATH

1. **Day 1**: Setup environment, install dependencies, run tests ✅
2. **Day 2**: Get YouTube credentials, authenticate, test in DRY_RUN mode
3. **Day 3**: Upload ONE private video to YouTube, verify it worked
4. **Week 2**: Build confidence with YouTube, add CLI/API interfaces
5. **Week 3+**: Only after YouTube is rock-solid, consider TikTok (with test account)
6. **Future**: Instagram is hardest - consider skipping or using official API (requires business account)

---

## 📞 GETTING HELP

If stuck:
1. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for known issues
2. Run verification commands to diagnose
3. Check logs (set `LOG_LEVEL=DEBUG` in `.env`)
4. Start with YouTube only - it's the most reliable
5. Read the error messages carefully

**Common Issues:**
- "client_secrets.json not found" → Place file in project root
- "No module named video_publisher" → Run `pip install -e .`
- YouTube quota exceeded → Wait 24 hours (free tier resets daily)
- TikTok/Instagram login failed → Use test accounts, expect challenges

---

## ✨ SUMMARY

**You must provide:**
- YouTube: `client_secrets.json` from Google Cloud Console
- Test videos in `data/videos/` directory
- `.env` file with your settings

**Recommended start:**
1. YouTube only (safest, official API)
2. Private uploads initially
3. Test with one video
4. Expand after confidence built

**Skip initially:**
- TikTok/Instagram (too risky)
- Public uploads
- Production accounts

**Your next command:**
```bash
# Start here:
cp .env.example .env
mkdir -p data/videos
# Then get YouTube credentials from Google Cloud Console
```

Good luck! Start with YouTube, keep it simple, and expand gradually. 🚀
