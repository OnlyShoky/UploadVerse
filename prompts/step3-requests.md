## CONTEXT
I'm working on implementing the Video Publisher project. Now I need clear guidelines on what resources YOU need from ME to make the project functional, and where I should provide them.

## TASK: CREATE USER RESOURCE REQUIREMENTS GUIDE

### 1. CREATE "USER_SETUP.md" FILE
Generate a comprehensive guide explaining:

**What I need to provide:**
1. **Credentials & API Keys** - What exact credentials are needed for each platform:
   - YouTube: Google Cloud Console credentials (client ID, secret, refresh token)
   - TikTok: Do I need Business API access? Or just account credentials for web automation?
   - Instagram: Personal credentials or Business account? Facebook Developer app setup?
   
2. **Media Files** - What video files I should have ready:
   - Format requirements (MP4, codecs, sizes)
   - Test video recommendations
   - Where to place sample videos

3. **Configuration Files** - What configs I need to create/modify:
   - `.env` file structure with my actual values
   - Browser profiles/cookies for TikTok/Instagram
   - Rate limiting settings

4. **Testing Resources** - What I need for testing:
   - Dummy accounts for safe testing
   - Test video files location
   - Mock data requirements

### 2. PROVIDE LOCATION GUIDE
Tell me EXACTLY where to put each resource:
```
project/
├── .env                    # My actual credentials (gitignored)
├── .env.example            # Template with placeholder values
├── config/
│   └── my-config.yaml     # My personal settings
├── data/
│   ├── cookies/           # Browser session data
│   ├── videos/            # My video files to upload
│   └── outputs/           # Processed videos
└── tests/
    └── fixtures/          # Test videos (can be small dummy files)
```

### 3. CREATE SETUP CHECKLIST
Provide a step-by-step checklist for me to complete:

**Phase 1: Account Setup**
- [ ] YouTube: Google Cloud Console project created
- [ ] YouTube: OAuth credentials obtained
- [ ] TikTok: Account ready (personal/business)
- [ ] Instagram: Account ready + Facebook Developer setup if needed

**Phase 2: File Organization**
- [ ] Create `.env` from `.env.example`
- [ ] Add videos to `data/videos/` directory
- [ ] Set up browser profiles if using automation

**Phase 3: Testing Readiness**
- [ ] Create test accounts for risky automation
- [ ] Prepare dummy videos for testing
- [ ] Configure safe mode for development

### 4. INCLUDE SAFETY WARNINGS
Clearly warn me about:
- NEVER committing real credentials to git
- Using burner/test accounts for TikTok/Instagram automation
- Understanding platform TOS risks
- Starting with YouTube-only setup for safety

### 5. PROVIDE TEMPLATES
Give me ready-to-use templates:

**.env template:**
```bash
# YouTube
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REFRESH_TOKEN=your_refresh_token_here

# TikTok (if using web automation)
TIKTOK_USERNAME=your_username
TIKTOK_PASSWORD=your_password

# Instagram
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Safety
TEST_MODE=true  # Start with this!
DRY_RUN=true    # Don't actually upload initially
```

**config/my-config.yaml template:**
```yaml
platforms:
  youtube:
    enabled: true
    upload_privacy: "private"  # Start with private uploads!
    
  tiktok:
    enabled: false  # Disable until tested
    use_test_account: true
    
  instagram:
    enabled: false  # Disable initially
```

### 6. EXPLAIN WHAT HAPPENS IF I DON'T PROVIDE SOMETHING
Tell me:
- Which features will work without my input
- What will use mocked/dummy data
- How to run the project in test/safe mode
- Minimum required setup to get started

### 7. CREATE VERIFICATION COMMANDS
Give me commands to verify my setup:
```bash
# Check if credentials are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('YouTube:', '✅' if os.getenv('YOUTUBE_CLIENT_ID') else '❌')"

# Check video directory
ls -la data/videos/*.mp4

# Test in safe mode
python -c "import os; os.environ['TEST_MODE']='true'; os.environ['DRY_RUN']='true'; print('Safe mode activated')"
```

## OUTPUT EXPECTED
Generate a complete `USER_SETUP.md` file that:
1. Clearly lists what I need to provide
2. Shows exactly where to put things
3. Includes templates I can copy-paste
4. Explains safety precautions
5. Provides verification steps
6. Manages expectations about what will work immediately

Be practical and honest. Tell me if certain features won't work without specific inputs from me.
```

---

# **QUICK VERSION (If you want more concise):**

```
Create a "What You Need to Provide" guide for the Video Publisher project. 

Tell me:
1. What credentials/files I must provide
2. Where exactly to put them in the project structure
3. What templates to copy and fill
4. Safety precautions (test accounts, private uploads first)
5. Minimum setup to get something working
6. Commands to verify my setup is correct

Be specific about:
- YouTube API credentials location (Google Cloud Console)
- Whether TikTok needs API keys or just account login
- Instagram requirements (personal vs business account)
- Where to place my video files
- How to run in test/safe mode first

Give me copy-paste templates for .env file and config files.
