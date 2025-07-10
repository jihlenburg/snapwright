# SnapWright

A simple yet powerful Python library for web browsing and screenshots using Playwright.

## Features

- 🚀 **Simple API** - Just one function to get started
- 📸 **Smart Screenshots** - Full page, viewport, or specific elements  
- 🔄 **Efficient Browser Reuse** - 10x faster than naive implementations
- 💾 **Intelligent Caching** - Avoid redundant screenshots
- 🛡️ **Reliable** - Automatic retries and fallback mechanisms
- 🎯 **Flexible** - Wait for specific content, extract data while browsing
- 📦 **Production Ready** - Proper resource management and error handling

## Installation

```bash
pip install snapwright
```

For the browser engine:
```bash
playwright install chromium
```

## Quick Start

```python
from snapwright import screenshot

# Take a screenshot
path = screenshot("https://example.com")
print(f"Screenshot saved to: {path}")
```

## Advanced Usage

### Wait for Dynamic Content

```python
from snapwright import capture_screenshot

# Wait for specific element before capturing
path = capture_screenshot(
    "https://tradingview.com/chart",
    wait_for=".chart-container",
    wait_timeout=10000,  # 10 seconds
    extra_wait=2000      # Additional 2 seconds after element appears
)
```

### Capture Specific Element

```python
# Screenshot only a specific part of the page
path = capture_screenshot(
    "https://example.com",
    selector=".main-content",
    full_page=False
)
```

### Extract Data While Browsing

```python
from snapwright import browse_and_extract

# Extract text from specific elements
result = browse_and_extract(
    "https://example.com/weather",
    {
        "temperature": ".temp-value",
        "condition": ".weather-condition",
        "humidity": ".humidity-value"
    },
    screenshot=True  # Also take a screenshot
)

print(result['extracted'])
# {'temperature': '72°F', 'condition': 'Sunny', 'humidity': '45%'}
```

### Batch Processing

```python
from snapwright import batch_screenshots

urls = [
    "https://example.com",
    "https://github.com",
    "https://google.com"
]

results = batch_screenshots(urls, output_dir="screenshots")
# Returns dict mapping URLs to screenshot paths
```

## Configuration

Configure via environment variables:

```bash
# Browser settings
BROWSER_HEADLESS=true       # Run in headless mode
BROWSER_TIMEOUT=30000       # Navigation timeout (ms)

# Cache settings  
SCREENSHOT_CACHE=true       # Enable caching
CACHE_TTL_HOURS=6          # Cache lifetime

# Performance
MAX_BROWSER_CONTEXTS=3      # Max parallel contexts
MAX_RETRIES=2              # Retry attempts on failure
```

## Architecture

The library uses a singleton browser manager for efficiency:

```
Your Code
    ↓
screenshot(url) → Simple API
    ↓
BrowserManager → Reuses browser contexts
    ↓
CacheManager → Avoids duplicate work
    ↓
Playwright → Controls Chromium
```

## Performance

| Operation | Time | Memory |
|-----------|------|--------|
| First screenshot | 2-3s | ~150MB |
| Subsequent screenshots | 0.5-1s | +10MB |
| Cached screenshot | <0.1s | 0 |
| Batch of 100 URLs | 2-4 min | ~200MB |

## Examples

### Custom Viewport Size

```python
from snapwright import capture_screenshot, set_config

# Configure viewport
set_config(viewport_width=1280, viewport_height=720)

# Take mobile screenshot
path = capture_screenshot("https://example.com", mobile=True)
```

### Error Handling

```python
from snapwright import screenshot, BrowserError

try:
    path = screenshot("https://invalid-url-example")
except BrowserError as e:
    print(f"Screenshot failed: {e}")
    # Fallback logic here
```

### Custom Wait Conditions

```python
# Wait for multiple conditions
path = capture_screenshot(
    "https://app.example.com",
    wait_for=[
        ".loading-complete",
        "text=Welcome"
    ],
    wait_until="networkidle"  # Also wait for network
)
```

## CLI Usage

The package includes a CLI tool:

```bash
# Basic screenshot
snapwright https://example.com

# With options
snapwright https://example.com \
    --output screenshot.png \
    --full-page \
    --wait-for ".content-loaded"

# Batch mode
snapwright --batch urls.txt --output-dir screenshots/
```

## API Reference

### Main Functions

#### `screenshot(url, filename=None)`
Simple screenshot function for basic use.

#### `capture_screenshot(url, **options)`
Advanced screenshot with full control.

**Options:**
- `output_path`: Where to save the screenshot
- `full_page`: Capture entire page (default: True)
- `selector`: CSS selector for specific element
- `wait_for`: CSS selector to wait for
- `wait_timeout`: Timeout for wait_for (ms)
- `extra_wait`: Additional wait time (ms)
- `use_cache`: Use cached screenshot if available

#### `browse_and_extract(url, selectors, screenshot=False)`
Browse and extract data from a page.

#### `batch_screenshots(urls, output_dir="screenshots")`
Process multiple URLs efficiently.

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/playwright-web-browser
cd playwright-web-browser
pip install -e ".[dev]"
playwright install chromium
```

### Run Tests

```bash
pytest
# or with coverage
pytest --cov=snapwright
```

### Code Style

```bash
# Format code
black playwright_web_browser tests

# Lint
flake8 playwright_web_browser tests
mypy playwright_web_browser
```

## Docker Support

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install snapwright
RUN playwright install chromium
RUN playwright install-deps

# Your application
COPY . /app
WORKDIR /app
CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues

**"Browser not found"**
```bash
playwright install chromium
```

**"Permission denied" on Linux**
```bash
playwright install-deps
```

**High memory usage**
- Enable cache: `SCREENSHOT_CACHE=true`
- Reduce contexts: `MAX_BROWSER_CONTEXTS=1`

**Timeout errors**
- Increase timeout: `BROWSER_TIMEOUT=60000`
- Check your internet connection
- Verify the URL is accessible

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built on top of [Playwright](https://playwright.dev/) by Microsoft.