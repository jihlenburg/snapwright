"""Core functionality for web browsing and screenshots."""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union, List

from playwright.sync_api import Page, Error as PlaywrightError

from .browser_manager import browser_manager
from .cache import screenshot_cache
from .config import browser_config
from .exceptions import (
    BrowserError, TimeoutError, NavigationError, 
    ElementNotFoundError, ScreenshotError
)

logger = logging.getLogger(__name__)


def capture_screenshot(
    url: str,
    output_path: Optional[Union[str, Path]] = None,
    full_page: bool = True,
    selector: Optional[str] = None,
    wait_for: Optional[Union[str, List[str]]] = None,
    wait_timeout: int = 5000,
    use_cache: bool = True,
    extra_wait: int = 0,
    mobile: bool = False,
    device_name: Optional[str] = None,
) -> Optional[Path]:
    """
    Capture a screenshot of a website or specific element.
    
    Args:
        url: Website URL to capture
        output_path: Where to save (optional, auto-generated if None)
        full_page: Capture entire scrollable page (True) or just viewport (False)
        selector: CSS selector for specific element (optional)
        wait_for: CSS selector(s) to wait for before capture (optional)
        wait_timeout: Timeout for wait_for selector (ms)
        use_cache: Use cached screenshot if available
        extra_wait: Additional wait time after page load (ms)
        mobile: Use mobile viewport
        device_name: Specific device to emulate (e.g., "iPhone 12")
    
    Returns:
        Path to screenshot file, or None if failed
        
    Examples:
        # Simple full page screenshot
        capture_screenshot("https://example.com")
        
        # Specific element
        capture_screenshot("https://example.com", selector=".main-content")
        
        # Wait for dynamic content
        capture_screenshot("https://example.com", wait_for=".chart-loaded")
        
        # Mobile screenshot
        capture_screenshot("https://example.com", mobile=True)
    """
    
    # Check cache first
    cache_options = {
        'full_page': full_page,
        'selector': selector,
        'mobile': mobile,
        'device_name': device_name
    }
    
    if use_cache:
        cached = screenshot_cache.get_cached_path(url, cache_options)
        if cached:
            logger.info(f"Using cached screenshot for {url}")
            if output_path and str(cached) != str(output_path):
                import shutil
                shutil.copy2(cached, output_path)
                return Path(output_path)
            return cached
    
    # Generate output path if not provided
    if output_path is None:
        timestamp = int(time.time())
        output_path = Path(browser_config.default_output_dir) / f"screenshot_{timestamp}.png"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Capture screenshot
    page = None
    for attempt in range(browser_config.max_retries):
        try:
            # Get browser context
            context = browser_manager.get_context()
            
            # Configure for mobile if requested
            if mobile or device_name:
                # Close and recreate context with device emulation
                devices = {
                    "iPhone 12": {"width": 390, "height": 844, "deviceScaleFactor": 3},
                    "iPad": {"width": 820, "height": 1180, "deviceScaleFactor": 2},
                    "Pixel 5": {"width": 393, "height": 851, "deviceScaleFactor": 2.75},
                }
                
                if device_name and device_name in devices:
                    device = devices[device_name]
                else:
                    device = {"width": 375, "height": 667, "deviceScaleFactor": 2}
                
                page = context.new_page(
                    viewport={'width': device['width'], 'height': device['height']},
                    device_scale_factor=device['deviceScaleFactor'],
                    is_mobile=True,
                    has_touch=True
                )
            else:
                page = context.new_page()
            
            # Navigate to URL
            logger.info(f"Navigating to {url}")
            try:
                page.goto(url, wait_until=browser_config.wait_until, timeout=browser_config.timeout)
            except PlaywrightError as e:
                raise NavigationError(f"Failed to navigate to {url}: {e}")
            
            # Wait for specific element(s) if requested
            if wait_for:
                wait_selectors = [wait_for] if isinstance(wait_for, str) else wait_for
                for wait_selector in wait_selectors:
                    logger.info(f"Waiting for selector: {wait_selector}")
                    try:
                        page.wait_for_selector(wait_selector, timeout=wait_timeout)
                    except PlaywrightError:
                        raise TimeoutError(f"Timeout waiting for selector: {wait_selector}")
            
            # Extra wait if needed
            if extra_wait > 0:
                page.wait_for_timeout(extra_wait)
            
            # Take screenshot
            try:
                if selector:
                    # Screenshot specific element
                    element = page.query_selector(selector)
                    if element:
                        element.screenshot(path=str(output_path))
                    else:
                        raise ElementNotFoundError(f"Selector '{selector}' not found")
                else:
                    # Full page or viewport screenshot
                    page.screenshot(
                        path=str(output_path),
                        full_page=full_page
                    )
            except PlaywrightError as e:
                raise ScreenshotError(f"Failed to capture screenshot: {e}")
            
            logger.info(f"Screenshot saved to {output_path}")
            
            # Save to cache
            if use_cache:
                screenshot_cache.save_to_cache(url, output_path, cache_options)
            
            return output_path
            
        except BrowserError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.warning(f"Screenshot attempt {attempt + 1} failed: {e}")
            if attempt == browser_config.max_retries - 1:
                logger.error(f"Failed to capture screenshot after {browser_config.max_retries} attempts")
                return None
        
        finally:
            if page:
                try:
                    page.close()
                except:
                    pass


def browse_and_extract(
    url: str,
    extract_selectors: Dict[str, str],
    screenshot: bool = False,
    screenshot_path: Optional[Path] = None,
    wait_for: Optional[str] = None,
    wait_timeout: int = 5000
) -> Dict[str, Any]:
    """
    Browse a website and extract data from specific elements.
    
    Args:
        url: Website URL
        extract_selectors: Dict mapping names to CSS selectors
        screenshot: Also take a screenshot
        screenshot_path: Where to save screenshot
        wait_for: Wait for selector before extracting
        wait_timeout: Timeout for wait_for
    
    Returns:
        Dict with extracted data and optional screenshot path
        
    Example:
        data = browse_and_extract(
            "https://example.com/weather",
            {
                "temperature": ".temp-value",
                "condition": ".weather-condition",
                "humidity": ".humidity-value"
            },
            screenshot=True
        )
    """
    result = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'extracted': {},
        'screenshot': None,
        'error': None
    }
    
    page = None
    try:
        context = browser_manager.get_context()
        page = context.new_page()
        
        # Navigate
        page.goto(url, wait_until=browser_config.wait_until, timeout=browser_config.timeout)
        
        # Wait for content if specified
        if wait_for:
            page.wait_for_selector(wait_for, timeout=wait_timeout)
        
        # Extract data
        for name, selector in extract_selectors.items():
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    if len(elements) == 1:
                        result['extracted'][name] = elements[0].text_content().strip()
                    else:
                        result['extracted'][name] = [el.text_content().strip() for el in elements]
                else:
                    result['extracted'][name] = None
            except Exception as e:
                result['extracted'][name] = f"Error: {str(e)}"
        
        # Take screenshot if requested
        if screenshot:
            if not screenshot_path:
                screenshot_path = Path(browser_config.default_output_dir) / f"browse_{int(time.time())}.png"
            
            page.screenshot(path=str(screenshot_path), full_page=True)
            result['screenshot'] = str(screenshot_path)
    
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Browse and extract failed: {e}")
    
    finally:
        if page:
            try:
                page.close()
            except:
                pass
    
    return result


def batch_screenshots(
    urls: List[str],
    output_dir: Union[str, Path] = None,
    full_page: bool = True,
    use_cache: bool = True,
    delay_between: int = 1000,
    name_prefix: str = "screenshot"
) -> Dict[str, Optional[Path]]:
    """
    Capture screenshots of multiple URLs efficiently.
    
    Args:
        urls: List of URLs to capture
        output_dir: Directory for screenshots
        full_page: Capture full page for all
        use_cache: Use cache if available
        delay_between: Delay between captures (ms)
        name_prefix: Prefix for generated filenames
    
    Returns:
        Dict mapping URLs to screenshot paths
    """
    if output_dir is None:
        output_dir = Path(browser_config.default_output_dir) / f"batch_{int(time.time())}"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for i, url in enumerate(urls):
        filename = f"{name_prefix}_{i:03d}_{int(time.time())}.png"
        output_path = output_dir / filename
        
        logger.info(f"Capturing {i+1}/{len(urls)}: {url}")
        
        screenshot_path = capture_screenshot(
            url,
            output_path=output_path,
            full_page=full_page,
            use_cache=use_cache
        )
        
        results[url] = screenshot_path
        
        # Delay between captures to be respectful
        if i < len(urls) - 1 and delay_between > 0:
            time.sleep(delay_between / 1000)
    
    return results


def screenshot(url: str, filename: Optional[str] = None) -> Optional[Path]:
    """
    Simple screenshot function for basic use.
    
    Examples:
        screenshot("https://example.com")
        screenshot("https://example.com", "example.png")
    """
    if filename:
        output_path = Path(browser_config.default_output_dir) / filename
    else:
        output_path = None
    
    return capture_screenshot(url, output_path=output_path)