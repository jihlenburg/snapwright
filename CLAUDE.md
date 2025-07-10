# CLAUDE.md - SnapWright Development Guide

## Project Overview

**SnapWright** is a Python library for web browsing and screenshots using Playwright, designed to be simple yet powerful.

- **Author**: Joern Ihlenburg
- **License**: MIT (© 2025)
- **GitHub**: https://github.com/jihlenburg/snapwright
- **Package**: `snapwright` on PyPI

## Quick Commands

```bash
# Development setup
cd ~/snapwright
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
playwright install chromium

# Run tests
pytest
pytest --cov=snapwright

# Format & lint
black src tests examples
flake8 src tests
mypy src

# Build package
python -m build

# Clean up
make clean
```

## Project Structure

```
snapwright/
├── src/snapwright/     # Main package code
│   ├── core.py        # Main API functions
│   ├── browser_manager.py  # Singleton browser management
│   ├── cache.py       # Screenshot caching
│   ├── config.py      # Configuration management
│   ├── cli.py         # Command-line interface
│   └── exceptions.py  # Custom exceptions
├── tests/             # Test suite
├── examples/          # Usage examples
└── docs/              # Documentation (if added)
```

## Core API

### Simple Usage
```python
from snapwright import screenshot

# Basic screenshot
path = screenshot("https://example.com")

# With filename
path = screenshot("https://example.com", "output.png")
```

### Advanced Usage
```python
from snapwright import capture_screenshot

# Full control
path = capture_screenshot(
    "https://example.com",
    full_page=True,
    wait_for=".content-loaded",
    selector=".specific-element",
    mobile=True
)
```

### Data Extraction
```python
from snapwright import browse_and_extract

data = browse_and_extract(
    "https://example.com",
    {
        "title": "h1",
        "price": ".price",
        "description": ".desc"
    }
)
```

## Development Workflow

### 1. Making Changes
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes, test locally
pytest tests/

# Commit with conventional commits
git add .
git commit -m "feat: add new screenshot option"
```

### 2. Testing
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_core.py::TestScreenshot

# With coverage
pytest --cov=snapwright --cov-report=html
```

### 3. Pre-Release Checklist
- [ ] Update version in `src/snapwright/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation/README if needed
- [ ] Ensure examples work

### 4. Release Process
```bash
# Tag release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Build and upload to PyPI
python -m build
python -m twine upload dist/*
```

## Architecture Notes

### Browser Manager (Singleton)
- Reuses browser contexts for efficiency
- Automatic cleanup on exit
- Configurable max contexts (default: 3)

### Caching System
- MD5-based cache keys
- Configurable TTL (default: 6 hours)
- Metadata tracking in JSON
- Automatic cleanup of old entries

### Configuration
- Environment variables supported
- Global config via `set_config()`
- Per-call overrides

### Error Handling
- Custom exception hierarchy
- Automatic retries (configurable)
- Graceful degradation

## Environment Variables

```bash
# Browser settings
export BROWSER_HEADLESS=true
export BROWSER_TIMEOUT=30000
export VIEWPORT_WIDTH=1920
export VIEWPORT_HEIGHT=1080

# Cache settings
export SCREENSHOT_CACHE=true
export CACHE_TTL_HOURS=6

# Performance
export MAX_BROWSER_CONTEXTS=3
export MAX_RETRIES=2
```

## Common Issues & Solutions

### Issue: "Browser not found"
```bash
playwright install chromium
playwright install-deps  # On Linux
```

### Issue: High memory usage
- Reduce MAX_BROWSER_CONTEXTS
- Enable caching
- Call browser_manager.cleanup() periodically

### Issue: Timeout errors
- Increase BROWSER_TIMEOUT
- Use wait_for with specific selectors
- Check network connectivity

## CLI Usage

```bash
# Simple screenshot
snapwright https://example.com

# Advanced options
snapwright https://example.com \
  --output screenshot.png \
  --full-page \
  --wait-for ".loaded" \
  --mobile

# Batch mode
snapwright --batch urls.txt --output-dir screenshots/
```

## Performance Tips

1. **Use caching** - Avoids redundant screenshots
2. **Batch requests** - More efficient than individual calls
3. **Reuse contexts** - Let browser manager handle lifecycle
4. **Specific selectors** - Faster than full page screenshots

## Future Enhancements

Consider adding:
- [ ] PDF generation support
- [ ] Video recording capability
- [ ] Network request interception
- [ ] Cookie/session management
- [ ] Proxy support
- [ ] Custom Chrome extensions

## Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set specific logger
logger = logging.getLogger('snapwright')
logger.setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

---

**Remember**: This is a production-ready library. Always test thoroughly and consider backwards compatibility when making changes.