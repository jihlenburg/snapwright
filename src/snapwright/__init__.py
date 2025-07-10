"""
SnapWright: Simple yet powerful web browsing and screenshot library.

Basic usage:
    from snapwright import screenshot
    
    path = screenshot("https://example.com")
"""

from .core import (
    screenshot,
    capture_screenshot,
    browse_and_extract,
    batch_screenshots,
)
from .browser_manager import BrowserManager, browser_manager
from .cache import ScreenshotCache, screenshot_cache
from .config import BrowserConfig, browser_config, set_config
from .exceptions import BrowserError, TimeoutError, NavigationError

__version__ = "0.1.0"

__all__ = [
    # Main functions
    "screenshot",
    "capture_screenshot",
    "browse_and_extract",
    "batch_screenshots",
    
    # Managers
    "BrowserManager",
    "browser_manager",
    "ScreenshotCache",
    "screenshot_cache",
    
    # Configuration
    "BrowserConfig",
    "browser_config",
    "set_config",
    
    # Exceptions
    "BrowserError",
    "TimeoutError",
    "NavigationError",
]