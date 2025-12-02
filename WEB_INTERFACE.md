# UploadVerse Web Interface

## 🎨 Minimalist Design
Elegant white background with Deep Navy (#1E40AF) accent color, clean typography (Inter font), and smooth transitions.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Web Server
```bash
python app.py
```

### 3. Open Your Browser
Navigate to: **http://localhost:5000**

## 📱 User Flow

### Step 1: Upload
- **Drag & drop** your video or click to browse
- Supports MP4, MOV, AVI up to 4GB
- Automatic format detection (16:9 or 9:16)
- Visual feedback during upload

### Step 2: Configure
- **Select platforms**: YouTube, TikTok, Instagram
- **Platform-specific metadata**:
  - YouTube: Title, description, tags, category, privacy
  - TikTok: Description, hashtags
  - Instagram: Caption, hashtags, location
- **Real-time credential status** for each platform
- Smart recommendations based on video format

### Step 3: Publish
- **Review** all settings before publishing
- **Progress tracking** with real-time updates
- **Success/error feedback** for each platform
- **Direct links** to uploaded videos

## 🔧 Features

### Drag & Drop Upload
- Beautiful drop zone with hover effects
- File validation (type, size)
- Preview with file information
- Easy file removal

### Smart Platform Selection
- Auto-suggestions based on video aspect ratio
- Connection status indicators  
- Warning badges for risky platforms (TikTok/Instagram)
- Toggle-based selection

### Dynamic Forms
- Platform-specific metadata forms
- Character counters for title/description
- Category and privacy dropdowns
- Tag suggestions

### Progress Tracking
- Visual progress bar
- Percentage updates
- Platform-specific results
- Direct video links

## 🎯 API Endpoints

### Web Routes
- `GET /` - Main upload page
- `POST /upload` - Handle file upload
- `GET /config/<file_id>` - Configuration page
- `POST /config/<file_id>` - Save configuration
- `GET /review/<file_id>` - Review page
- `POST /publish/<file_id>` - Start publish process

### REST API
- `POST /api/upload` - Upload via API
- `GET /api/status/<upload_id>` - Get upload status
- `GET /api/platforms` - List platforms
- `GET /api/metrics` - System metrics
- `GET /api/health` - Health check

## 📂 Project Structure

```
UploadVerse/
├── app.py                      # Main Flask application
├── upload_manager.py           # File upload handling
├── api/
│   ├── web_routes.py          # Web UI routes
│   ├── api_routes.py          # REST API routes
│   ├── templates/
│   │   ├── base.html          # Base template
│   │   ├── index.html         # Upload page
│   │   ├── config.html        # Configuration page
│   │   └── publish.html       # Publish/results page
│   └── static/
│       ├── css/
│       │   └── main.css       # Minimalist design system
│       └── js/
│           └── uploads.js     # Drag & drop functionality
└── src/
    └── video_publisher/       # Backend engine
```

## 🎨 Design System

### Colors
- **Primary**: #1E40AF (Deep Navy)
- **Background**: #FFFFFF (White)
- **Text**: #111827 (Dark Gray)
- **Success**: #10B981 (Green)
- **Warning**: #F59E0B (Amber)
- **Error**: #DC2626 (Red)

### Typography
- **Font**: Inter (Google Fonts)
- **Sizes**: Responsive with clear hierarchy

### Components
- Buttons (Primary, Secondary, Icon)
- Forms (Input, Textarea, Select)
- Cards (Video, Platform, Review)
- Badges (Status, Format)
- Progress bars

## 📱 Responsive Design
- Desktop-first with mobile support
- Breakpoint at 768px
- Touch-friendly interactions
- Optimized for screens down to 320px

## 🔐 Security
- CSRF protection via Flask sessions
- File type validation
- File size limits (4GB)
- Secure filename handling
- OAuth2 for YouTube
- Rate limiting via backend

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (Docker)
```bash
docker-compose up -d
```

### Production (Manual)
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Test Web Interface
1. Start server: `python app.py`
2. Open browser: http://localhost:5000
3. Upload a test video
4. Verify workflow

### Test API
```bash
curl -X POST -F "video=@test.mp4" http://localhost:5000/api/upload
```

## 📖 Documentation
- [Main README](../README.md)
- [YouTube Setup](../YOUTUBE_SETUP.md)
- [Safety Guide](../SAFETY.md)
- [User Setup](../USER_SETUP.md)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Template Not Found
- Check `app.py` has correct `template_folder` path
- Verify templates are in `api/templates/`

### Static Files Not Loading
- Check `app.py` has correct `static_folder` path
- Clear browser cache

### Upload Fails
- Check file size < 4GB
- Verify file type is MP4, MOV, or AVI
- Check `uploads/` directory exists and is writable

## 💡 Tips
- Use **private uploads** when testing YouTube
- Test with **small videos** first (~10MB)
- Check **credentials status** before publishing
- **Rate limits** reset daily
- Use **TikTok/Instagram** with test accounts only

## 🎯 Next Steps
1. Authenticate with YouTube (see YOUTUBE_SETUP.md)
2. Upload a test video
3. Publish to platforms
4. Monitor results in platform dashboards

---

**Version**: 0.1.0  
**License**: MIT  
**Author**: UploadVerse Team
