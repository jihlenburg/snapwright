"""Configuration management for playwright-web-browser."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BrowserConfig:
    """Configuration for browser operations."""
    
    # Browser settings
    headless: bool = True
    timeout: int = 30000  # 30 seconds
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Cache settings
    cache_enabled: bool = True
    cache_dir: str = "cache/screenshots"
    cache_ttl_hours: int = 6
    
    # Resource limits
    max_contexts: int = 3
    max_retries: int = 2
    
    # Behavior
    wait_until: str = "networkidle"  # or "load", "domcontentloaded"
    ignore_https_errors: bool = True
    
    # Paths
    downloads_dir: str = "temp/downloads"
    default_output_dir: str = "screenshots"
    
    # Browser launch args
    browser_args: list = field(default_factory=lambda: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
    ])
    
    @classmethod
    def from_env(cls) -> "BrowserConfig":
        """Create config from environment variables."""
        return cls(
            headless=os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
            timeout=int(os.getenv("BROWSER_TIMEOUT", "30000")),
            viewport_width=int(os.getenv("VIEWPORT_WIDTH", "1920")),
            viewport_height=int(os.getenv("VIEWPORT_HEIGHT", "1080")),
            cache_enabled=os.getenv("SCREENSHOT_CACHE", "true").lower() == "true",
            cache_dir=os.getenv("CACHE_DIR", "cache/screenshots"),
            cache_ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "6")),
            max_contexts=int(os.getenv("MAX_BROWSER_CONTEXTS", "3")),
            max_retries=int(os.getenv("MAX_RETRIES", "2")),
            wait_until=os.getenv("WAIT_UNTIL", "networkidle"),
            ignore_https_errors=os.getenv("IGNORE_HTTPS_ERRORS", "true").lower() == "true",
        )
    
    def update(self, **kwargs):
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration option: {key}")


# Global config instance
browser_config = BrowserConfig.from_env()


def set_config(**kwargs):
    """
    Update global browser configuration.
    
    Examples:
        set_config(headless=False)
        set_config(viewport_width=1280, viewport_height=720)
    """
    browser_config.update(**kwargs)