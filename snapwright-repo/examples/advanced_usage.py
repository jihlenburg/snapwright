#!/usr/bin/env python3
"""Advanced usage examples for SnapWright."""

from snapwright import (
    capture_screenshot, 
    browse_and_extract,
    browser_manager,
    screenshot_cache,
    set_config
)
import time
from pathlib import Path


def example_configuration():
    """Show how to customize configuration."""
    print("1. Custom Configuration")
    
    # Change configuration globally
    set_config(
        headless=False,  # Show browser window
        viewport_width=1280,
        viewport_height=720,
        cache_ttl_hours=12,
        max_retries=3
    )
    
    # Take screenshot with new config
    path = capture_screenshot("https://example.com")
    print(f"   Screenshot with custom config: {path}")
    
    # Reset to defaults
    set_config(headless=True, viewport_width=1920, viewport_height=1080)


def example_cache_management():
    """Demonstrate cache management features."""
    print("\n2. Cache Management")
    
    # Get cache statistics
    stats = screenshot_cache.get_cache_stats()
    print("   Cache statistics:")
    print(f"   - Total entries: {stats['total_entries']}")
    print(f"   - Total size: {stats['total_size_mb']:.2f} MB")
    print(f"   - Cache directory: {stats['cache_dir']}")
    
    # Take some screenshots to populate cache
    urls = ["https://example.com", "https://github.com", "https://python.org"]
    for url in urls:
        capture_screenshot(url, use_cache=True)
    
    # Clean up old cache entries
    screenshot_cache.cleanup_old_cache()
    print("   Cleaned up old cache entries")
    
    # Force clear all cache if needed
    # screenshot_cache.clear_cache()
    # print("   Cleared all cache")


def example_parallel_processing():
    """Show how to process multiple URLs in parallel."""
    print("\n3. Parallel Processing")
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    urls = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://python.org",
        "https://djangoproject.com"
    ]
    
    def capture_with_timing(url):
        start = time.time()
        path = capture_screenshot(url, use_cache=False)
        duration = time.time() - start
        return url, path, duration
    
    # Process URLs in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(capture_with_timing, url): url for url in urls}
        
        for future in as_completed(futures):
            url, path, duration = future.result()
            print(f"   {url} -> {duration:.2f}s")


def example_custom_wait_conditions():
    """Advanced waiting strategies for complex pages."""
    print("\n4. Custom Wait Conditions")
    
    # Wait for multiple elements
    result = browse_and_extract(
        "https://example.com/complex",
        {
            "header": "h1",
            "content": ".main-content",
            "sidebar": ".sidebar"
        },
        wait_for=[".header-loaded", ".content-loaded", ".sidebar-loaded"],
        wait_timeout=20000
    )
    
    print("   Extracted after complex wait:")
    for key, value in result['extracted'].items():
        print(f"   - {key}: {value[:30]}..." if value else f"   - {key}: None")


def example_browser_lifecycle():
    """Demonstrate browser lifecycle management."""
    print("\n5. Browser Lifecycle Management")
    
    # The browser manager is a singleton
    print("   Browser manager handles lifecycle automatically")
    
    # Take multiple screenshots - reuses browser
    for i in range(3):
        start = time.time()
        path = capture_screenshot(f"https://example.com/page{i}")
        duration = time.time() - start
        print(f"   Screenshot {i+1}: {duration:.2f}s")
    
    # Manual cleanup if needed (usually automatic on exit)
    # browser_manager.cleanup()
    # print("   Browser cleaned up manually")


def example_error_recovery():
    """Show error recovery and retry mechanisms."""
    print("\n6. Error Recovery")
    
    from snapwright import BrowserError
    
    # Configure for testing
    set_config(max_retries=3, timeout=5000)
    
    problematic_urls = [
        "https://this-domain-does-not-exist-12345.com",
        "https://example.com/404",
        "https://httpstat.us/500"  # Returns 500 error
    ]
    
    for url in problematic_urls:
        print(f"   Attempting: {url}")
        try:
            path = capture_screenshot(url, use_cache=False)
            print(f"   Success: {path}")
        except BrowserError as e:
            print(f"   Failed as expected: {type(e).__name__}")
        except Exception as e:
            print(f"   Unexpected error: {e}")


def example_custom_output_organization():
    """Organize screenshots in a custom structure."""
    print("\n7. Custom Output Organization")
    
    from datetime import datetime
    
    # Create organized directory structure
    base_dir = Path("screenshots_organized")
    
    sites = {
        "search": ["https://google.com", "https://duckduckgo.com"],
        "social": ["https://twitter.com", "https://linkedin.com"],
        "dev": ["https://github.com", "https://stackoverflow.com"]
    }
    
    for category, urls in sites.items():
        category_dir = base_dir / category / datetime.now().strftime("%Y-%m-%d")
        category_dir.mkdir(parents=True, exist_ok=True)
        
        for url in urls:
            domain = url.split("//")[1].split("/")[0]
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{domain}_{timestamp}.png"
            
            path = capture_screenshot(
                url,
                output_path=category_dir / filename,
                full_page=False  # Just viewport for overview
            )
            print(f"   {category}/{domain} -> {path}")


def example_monitoring_workflow():
    """Example of a monitoring workflow."""
    print("\n8. Monitoring Workflow")
    
    import json
    from datetime import datetime
    
    # Define what to monitor
    monitor_config = {
        "name": "Example Site Monitor",
        "url": "https://example.com",
        "checks": {
            "title": "h1",
            "last_updated": ".last-updated",
            "status": ".service-status",
            "metrics": ".metrics-value"
        },
        "screenshot": True
    }
    
    # Run monitoring check
    timestamp = datetime.now()
    result = browse_and_extract(
        monitor_config["url"],
        monitor_config["checks"],
        screenshot=monitor_config["screenshot"],
        screenshot_path=f"monitoring/example_{timestamp:%Y%m%d_%H%M%S}.png"
    )
    
    # Save monitoring results
    monitor_result = {
        "timestamp": timestamp.isoformat(),
        "config": monitor_config,
        "result": result
    }
    
    # Save to JSON file
    output_file = Path(f"monitoring/results_{timestamp:%Y%m%d}.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, "a") as f:
        f.write(json.dumps(monitor_result) + "\n")
    
    print(f"   Monitoring result saved to: {output_file}")
    print(f"   Screenshot: {result.get('screenshot')}")


if __name__ == "__main__":
    print("=== Advanced Usage Examples ===\n")
    
    # Run all examples
    example_configuration()
    example_cache_management()
    example_parallel_processing()
    example_custom_wait_conditions()
    example_browser_lifecycle()
    example_error_recovery()
    example_custom_output_organization()
    example_monitoring_workflow()
    
    print("\n✅ All advanced examples completed!")