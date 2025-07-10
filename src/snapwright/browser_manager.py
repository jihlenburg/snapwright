"""Singleton browser manager for efficient resource usage."""

import atexit
import logging
from threading import Lock
from typing import Optional, List

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright, Error

from .config import browser_config
from .exceptions import BrowserError

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages a single browser instance with multiple contexts."""
    
    _instance: Optional["BrowserManager"] = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.contexts: List[BrowserContext] = []
        self._initialized = True
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def get_browser(self) -> Browser:
        """Get or create browser instance."""
        if not self.browser:
            logger.info("Starting Playwright browser")
            try:
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch(
                    headless=browser_config.headless,
                    args=browser_config.browser_args
                )
            except Error as e:
                raise BrowserError(f"Failed to launch browser: {e}")
        return self.browser
    
    def get_context(self) -> BrowserContext:
        """Get a browser context, reusing if possible."""
        # Clean up closed contexts
        self.contexts = [ctx for ctx in self.contexts if ctx.pages]
        
        # Reuse existing context if available
        for context in self.contexts:
            if len(context.pages) == 0:  # No active pages
                return context
        
        # Create new context if under limit
        if len(self.contexts) < browser_config.max_contexts:
            browser = self.get_browser()
            context = browser.new_context(
                viewport={
                    'width': browser_config.viewport_width,
                    'height': browser_config.viewport_height
                },
                ignore_https_errors=browser_config.ignore_https_errors,
                accept_downloads=True,
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            )
            self.contexts.append(context)
            logger.debug(f"Created new browser context (total: {len(self.contexts)})")
            return context
        
        # Otherwise use the least busy context
        return min(self.contexts, key=lambda c: len(c.pages))
    
    def cleanup(self):
        """Clean up all resources."""
        logger.info("Cleaning up browser resources")
        
        # Close all contexts
        for context in self.contexts:
            try:
                context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
        
        # Close browser
        if self.browser:
            try:
                self.browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
        
        # Stop playwright
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
        
        self.contexts.clear()
        self.browser = None
        self.playwright = None
    
    def reset(self):
        """Reset the browser manager, closing all resources."""
        self.cleanup()
        self._initialized = False
        self.__init__()


# Global instance
browser_manager = BrowserManager()