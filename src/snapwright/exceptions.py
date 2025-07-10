"""Custom exceptions for playwright-web-browser."""


class BrowserError(Exception):
    """Base exception for browser-related errors."""
    pass


class TimeoutError(BrowserError):
    """Raised when a browser operation times out."""
    pass


class NavigationError(BrowserError):
    """Raised when navigation to a URL fails."""
    pass


class ElementNotFoundError(BrowserError):
    """Raised when a specified element cannot be found."""
    pass


class ScreenshotError(BrowserError):
    """Raised when screenshot capture fails."""
    pass


class CacheError(BrowserError):
    """Raised when cache operations fail."""
    pass