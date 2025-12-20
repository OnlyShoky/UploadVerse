# Instagram Setup

> **DANGER**: Instagram aggressively bans automation. Account bans are almost guaranteed. NEVER use your personal account.

## Requirements

- Instagram account (create a brand new test one)
- Chrome browser installed
- Patience for CAPTCHAs and challenges

## Configuration

Add to `.env`:
```bash
# Global Browser Settings (recommended)
HEADLESS=true
```

## Authenticate

```bash
# Using CLI
# NOTE: Use --no-headless for initial login to solve CAPTCHAs
video-publisher auth instagram --no-headless
```

**What happens:**
1. Chrome browser opens
2. Navigates to Instagram.com
3. Attempts login with credentials
4. You'll likely face:
   - CAPTCHA (solve manually)
   - SMS verification (enter code)
   - "Is this you?" prompts
   - Email verification
5. After successful login, cookies saved to `data/sessions/instagram_session.pkl`

## Upload Example

```bash
video-publisher upload vertical_video.mp4 --platforms instagram
```

**Note:** Instagram requires 9:16 vertical videos for Reels.

## How It Works

- Uses `undetected-chromedriver` for stealth automation
- Attempts to evade Instagram's bot detection
- Saves session cookies
- Expects frequent re-authentication
- Account bans are the norm, not the exception

## File Structure

```
UploadVerse/
├── .env
├── data/
│   └── sessions/
│       └── instagram_session.pkl  ← Created by auth
└── vertical_video.mp4
```

## Recommendations

1. **Create 2-3 test accounts** - you'll need backups
2. **Wait 48 hours** after account creation before automating
3. **Post manually first** - 1-2 posts to look like a real account
4. **Expect bans** - this is not reliable for production
5. **Consider official Facebook/Instagram Graph API** instead

## Troubleshooting

**"Challenge required"**: Complete the challenge manually in the browser
**Account locked**: Wait 24 hours or create new account
**Session expires quickly**: Re-run `auth instagram` before each upload
