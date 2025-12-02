# TikTok Setup

> **WARNING**: TikTok automation violates their Terms of Service. Use test accounts only. Account bans are common.

## Requirements

- TikTok account (create a test one, NOT your personal account)
- Chrome browser installed

## Configuration

Add to `.env`:
```bash
TIKTOK_USERNAME=your_test_username
TIKTOK_PASSWORD=your_test_password  # Optional, for programmatic login
TIKTOK_HEADLESS=false  # Keep false to see browser for CAPTCHA solving
```

## Authenticate

```bash
# Using CLI
video-publisher auth tiktok
```

**What happens:**
1. Chrome browser opens
2. Navigates to TikTok.com
3. If not logged in, log in manually
4. CAPTCHA may appear - solve it manually
5. Session cookies saved to `data/sessions/tiktok_session.pkl`

**Note:** You must log in manually in the browser window that opens. The script waits up to 60 seconds.

## Upload Example

```bash
video-publisher upload vertical_video.mp4 --platforms tiktok
```

## How It Works

- Uses `undetected-chromedriver` for stealth automation
- Saves browser cookies for session persistence
- Requires manual intervention for CAPTCHAs
- Account bans are likely with heavy use

## File Structure

```
UploadVerse/
├── .env
├── data/
│   └── sessions/
│       └── tiktok_session.pkl  ← Created by auth
└── vertical_video.mp4
```

## Troubleshooting

**"Login timeout"**: Log in faster (within 60 seconds)
**CAPTCHA keeps appearing**: Normal - solve it each time
**Account banned**: Expected - use different test account
