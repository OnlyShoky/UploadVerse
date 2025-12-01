# Testing Guide for Video Publisher

This directory contains all tests for the Video Publisher project.

## Test Files

### Unit Tests

#### `test_core.py`
Tests for the core engine components.

**What it tests:**
- `VideoAnalyzer`: Video metadata extraction
- `PlatformRouter`: Platform routing based on video aspect ratio
- `VideoPublisher`: Main engine orchestration

**Run:**
```bash
pytest tests/test_core.py -v
```

**Status**: ✅ All 5 tests passing

---

#### `test_platforms.py`
Tests for platform uploader implementations.

**What it tests:**
- `BasePlatform`: Abstract interface verification
- `YouTubeUploader`: OAuth2 authentication, upload logic
- `TikTokUploader`: Browser automation, session management
- `InstagramUploader`: Browser automation, Reels upload

**Run:**
```bash
pytest tests/test_platforms.py -v
```

**Status**: ✅ All 11 tests passing (mocked - no real uploads)

**Note**: All tests use mocks. No actual platform uploads are performed.

---

#### `test_interfaces.py`
Tests for the three interfaces (Library, CLI, Web API).

**What it tests:**
- Library interface: `upload_video()`, `get_publisher()`
- CLI commands: upload, status, version
- Web API endpoints: `/upload`, `/status`, `/platforms`, `/health`

**Run:**
```bash
pytest tests/test_interfaces.py -v
```

**Status**: ⚠️ 10/12 tests passing (2 failures in library interface mocks)

---

### Integration/Manual Tests

#### `test_credentials.py`
Credential validation and authentication testing (not a pytest file).

**What it does:**
- Verifies platform credentials are configured correctly
- Tests authentication without uploading videos
- Provides clear feedback on what's ready vs what needs setup

**Modes:**
- **Safe mode** (default): Only checks if credential files exist
- **Verify mode** (`--verify`): Actually attempts authentication (opens browsers for TikTok/IG)

**Usage:**
```bash
# Safe mode - just check files
python tests/test_credentials.py

# Test specific platform
python tests/test_credentials.py --platform youtube

# Verify authentication (WARNING: Opens browsers, may trigger anti-bot)
python tests/test_credentials.py --verify

# Verify specific platform
python tests/test_credentials.py --platform youtube --verify
```

**When to use:**
- Before first upload attempt
- After changing credentials
- When troubleshooting authentication issues
- To verify setup is correct

**Output:**
- ✅ Green: Ready to use
- ⚠️ Yellow: Needs setup
- ❌ Red: Error/not configured

---

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run with coverage:
```bash
pytest tests/ --cov=video_publisher --cov-report=html
```

### Run specific test:
```bash
pytest tests/test_core.py::test_video_analyzer_analyze -v
```

### Run tests matching pattern:
```bash
pytest tests/ -k "youtube" -v
```

---

## Test Structure

```
tests/
├── README.md                    # This file
├── test_core.py                 # Core engine tests (pytest)
├── test_platforms.py            # Platform uploader tests (pytest)
├── test_interfaces.py           # Interface tests (pytest)
├── test_credentials.py          # Credential validation (manual/integration)
└── fixtures/                    # Test data (optional)
    └── dummy_video.mp4          # Small test video
```

---

## Test Coverage Summary

| Component | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| Core Engine | 5 | ✅ Passing | High |
| Platform Uploaders | 11 | ✅ Passing (mocked) | High |
| Interfaces | 12 | ⚠️ 10/12 passing | Medium |
| **Total** | **28** | **26/28 passing** | **93%** |

---

## Known Test Issues

1. **`test_interfaces.py`**: 2 mock assertion failures
   - `test_library_upload_video_with_platforms`
   - `test_library_upload_video_auto_detect`
   - Need to fix mock setup

2. **Platform tests are mocked**: No real uploads tested
   - YouTube: Never tested with real OAuth2
   - TikTok: Never tested with real browser session
   - Instagram: Never tested with real account

---

## Testing Best Practices

### Before Committing:
```bash
# Run all automated tests
pytest tests/test_*.py

# Run credentials test in safe mode
python tests/test_credentials.py
```

### Before First Real Upload:
```bash
# Verify credentials
python tests/test_credentials.py --platform youtube --verify
```

### When Adding New Features:
1. Write tests first (TDD)
2. Ensure all existing tests still pass
3. Add integration test if needed
4. Update this README with new test info

---

## Troubleshooting Tests

### Tests fail to import video_publisher:
```bash
# Install in editable mode
pip install -e .
```

### Pytest not found:
```bash
# Install dev dependencies
pip install -r requirements-dev.txt
```

### Mock errors:
- Check that you're using correct patch targets
- Verify module paths match actual code structure

### Credentials test can't find .env:
```bash
# Create .env from template
cp .env.example .env
# Fill in your credentials
```

---

## Future Test Additions

- [ ] End-to-end upload test with real credentials (manual)
- [ ] Performance/load testing
- [ ] Error recovery testing
- [ ] Rate limiting tests
- [ ] Docker container tests

---

## Quick Reference

```bash
# Most common commands

# All unit tests
pytest tests/test_*.py -v

# Check credentials setup
python tests/test_credentials.py

# Test YouTube auth (safe)
python tests/test_credentials.py --platform youtube

# Full verification (opens browsers!)
python tests/test_credentials.py --verify
```
