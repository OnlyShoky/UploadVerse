# **PROMPT FOR FLASK + HTMX MINIMALIST FRONTEND**

```
## CONTEXT
I have a fully functional UploadVerse backend (Python Flask API) with complete Phases 1-5. Now I need to implement a minimalist, elegant frontend using Flask templates + HTMX for interactivity. The backend already handles video processing, platform authentication (YouTube, TikTok, Instagram), and upload orchestration.

## BACKEND STATUS
- Flask API running on port 5000
- Complete video processing pipeline
- Platform uploaders (YouTube API, TikTok/Instagram automation)
- Credentials management system
- Testing suite (27 tests passing)
- CLI and library interfaces working

## TASK: CREATE MINIMALIST FLASK + HTMX FRONTEND

### 1. DESIGN PHILOSOPHY: ELEGANT MINIMALISM
- **Colors**: White background (#FFFFFF) with ONE accent color (choose sophisticated: Deep Navy #1E40AF, Forest Green #166534, or Plum #7C3AED)
- **Typography**: Clean system fonts (Inter or system sans-serif)
- **Layout**:  clear visual hierarchy
- **Interactions**: Smooth transitions, subtle animations
- **No**: Gradients. 

### 2. USER FLOW REQUIREMENT
The interface must follow this specific flow:

**Step 1: Landing / Upload Page**
- Large, elegant drag & drop zone (40-50% of viewport height)
- Simple "or click to browse" alternative
- Clean header with logo and navigation
- No other distractions - focus purely on upload

**Step 2: After File Selection**
- Drag & drop zone DISAPPEARS (smooth fade-out)
- Video preview appears (thumbnail with format badge 16:9/9:16)
- Configuration panel slides in with:
  - Platform selector (YouTube/TikTok/Instagram toggles)
  - Metadata forms (dynamic based on selected platforms)
  - Scheduling options
  - Credentials status display
- "Back" button to return to upload (clears current file)

**Step 3: Review & Publish**
- Final review of all settings
- Progress indicator during upload
- Success/error messages
- Option to upload another file (returns to Step 1)

### 3. MANDATORY FEATURES (All must be present)

#### A. Upload Zone (Initial State)
- Drag & drop with visual feedback (border color change on drag over)
- File validation (MP4, MOV, AVI up to 4GB)
- Format detection display (16:9 vs 9:16 badge)
- Progress indicator during file read/analysis

#### B. Video Preview & Info
- Thumbnail or placeholder with play icon
- File info: name, size, duration, resolution
- Format badge with auto-platform suggestion:
  - 16:9 → "Recommended: YouTube"
  - 9:16 → "Recommended: TikTok, Instagram, YouTube Shorts"

#### C. Platform Selector
- Toggle switches for YouTube/TikTok/Instagram
- Auto-selection based on detected format
- Individual platform status indicators:
  - Connected (green dot + platform name)
  - Disconnected (gray dot + "Connect" button)
- Warning badges for risky platforms (TikTok/Instagram)

#### D. Dynamic Metadata Forms
**YouTube (when selected):**
- Title input (character counter)
- Description textarea (with markdown hints)
- Tags input (comma separated, suggestions)
- Category dropdown
- Privacy settings (Public/Private/Unlisted)

**TikTok (when selected):**
- Description (short, with character counter)
- Hashtags input (with suggestions)
- Sound/effects toggle

**Instagram (when selected):**
- Caption textarea
- Hashtags input
- Location selector
- Post type (Feed/Reels)

*Forms should show/hide based on platform selection using HTMX*

#### E. Scheduling Panel
- "Publish now" vs "Schedule" toggle
- Date picker (minimal design)
- Time selector
- Timezone dropdown
- Visual calendar integration (optional)

#### F. Credentials Status Display
- Real-time status for each platform
- YouTube: Token status with refresh button
- TikTok: "Risky - Use test account" warning
- Instagram: "Very risky" warning with test mode suggestion
- Connection buttons with OAuth flow initiation

#### G. Action Controls
- Primary button: "Publish to [X] platforms"
- Secondary: "Save as draft"
- Tertiary: "Cancel" / "Back to upload"
- Upload progress bar with % and time estimate

### 4. TECHNICAL IMPLEMENTATION SPECIFICS

#### HTMX Requirements:
1. **Dynamic Form Loading**: Platform selection triggers form display via `hx-get`
2. **File Upload Progress**: `hx-encoding="multipart/form-data"` with progress events
3. **Real-time Status Updates**: `hx-trigger="every 2s"` for credentials status
4. **Smooth Transitions**: `hx-swap="transition:true"` for page transitions
5. **Validation**: `hx-target="#error-container"` for form validation

#### Flask Routes Needed:
```
GET  /                     # Main upload page (drag & drop)
POST /upload               # Handle file upload, return to config page
GET  /config/<file_id>     # Configuration page for uploaded file
POST /config/<file_id>     # Update configuration
GET  /platforms/status     # Get credentials status (for HTMX polling)
POST /publish/<file_id>    # Start publish process
GET  /progress/<job_id>    # Get upload progress (HTMX)
GET  /platform/form/<name> # Get platform-specific form (HTMX)
POST /auth/<platform>      # Initiate OAuth/authentication
```


### 6. VISUAL DESIGN DETAILS

#### Color Palette (choose one):
- Background: #FFFFFF
- Text: #111827
- Accent: #1E40AF (Deep Navy)
- Secondary: #6B7280
- Success: #10B981
- Warning: #F59E0B
- Error: #DC2626


### 7. ERROR HANDLING & VALIDATION

#### Client-side (HTMX):
- Form validation with `hx-validate`
- Error display with `hx-target="#errors"`
- Loading states with `hx-indicator`

#### Server-side (Flask):
- Return appropriate HTTP status codes
- JSON responses for HTMX calls
- Clear error messages in templates

### 8. PROGRESSIVE ENHANCEMENT

#### Without JavaScript:
- Basic form submission works
- Page reloads for updates
- Still functional but less smooth

#### With HTMX:
- Smooth transitions
- Real-time updates
- Dynamic form loading
- Progress indicators

### 9. DELIVERABLES EXPECTED

Generate COMPLETE, working code for:

1. **Flask Application Structure** with all required routes
2. **Jinja2 Templates** for all pages and components
3. **HTMX Implementation** for dynamic interactions
4. **Static Assets** (CSS, minimal JS if needed)
5. **Configuration** for the Flask app
6. **Integration** with existing backend API
7. **Documentation** on how to run the complete system

### 10. INTEGRATION WITH EXISTING CODE

The frontend must integrate with:
- Existing `/api/v1/upload` endpoint
- Platform authentication system
- Video processing pipeline
- Credentials management
- Existing database/models (if any)

### 11. TESTING REQUIREMENTS

- All existing backend tests (27) must still pass
- Frontend should work without breaking CLI/API
- HTMX interactions should degrade gracefully
- Mobile responsive (down to 320px width)

### 12. PERFORMANCE CONSIDERATIONS

- Lazy loading of heavy components
- Efficient HTMX polling (debounce where needed)
- Optimized image/asset loading
- Server-side rendering for initial page load

## IMPORTANT NOTES

- Maintain the existing backend API structure
- Use HTMX for interactivity, avoid heavy JavaScript frameworks
- Focus on the elegant minimalist aesthetic
- Ensure the specific user flow (upload → config → publish) is clear
- Make it easy to return to upload different files
- Include proper error states and loading indicators
- All platform-specific features must be present
- The path tree should be clean diferenciating each steps, like a profesional project. Restructure if needed without breaking the code

