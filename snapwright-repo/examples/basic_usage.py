#!/usr/bin/env python3
"""Basic usage examples for SnapWright."""

from snapwright import screenshot, capture_screenshot


def example_simple_screenshot():
    """The simplest way to take a screenshot."""
    print("1. Simple screenshot")
    
    # Just provide a URL
    path = screenshot("https://example.com")
    print(f"   Screenshot saved to: {path}")
    
    # With a custom filename
    path = screenshot("https://example.com", "my_screenshot.png")
    print(f"   Custom filename: {path}")


def example_full_control():
    """Using capture_screenshot for more control."""
    print("\n2. Advanced screenshot options")
    
    # Viewport only (not full page)
    path = capture_screenshot(
        "https://example.com",
        full_page=False,
        output_path="viewport_only.png"
    )
    print(f"   Viewport screenshot: {path}")
    
    # Specific element
    path = capture_screenshot(
        "https://example.com",
        selector="h1",  # Capture just the H1 element
        output_path="header_only.png"
    )
    print(f"   Element screenshot: {path}")


def example_dynamic_content():
    """Handling dynamic content that loads after page load."""
    print("\n3. Dynamic content handling")
    
    # Wait for specific element to appear
    path = capture_screenshot(
        "https://www.tradingview.com/chart/",
        wait_for="canvas",  # Wait for chart canvas
        wait_timeout=15000,  # Wait up to 15 seconds
        extra_wait=2000,     # Then wait 2 more seconds
        output_path="chart_screenshot.png"
    )
    print(f"   Dynamic content screenshot: {path}")


def example_mobile_screenshots():
    """Taking mobile screenshots."""
    print("\n4. Mobile screenshots")
    
    # Generic mobile viewport
    path = capture_screenshot(
        "https://example.com",
        mobile=True,
        output_path="mobile_generic.png"
    )
    print(f"   Mobile screenshot: {path}")
    
    # Specific device
    path = capture_screenshot(
        "https://example.com",
        device_name="iPhone 12",
        output_path="iphone12.png"
    )
    print(f"   iPhone 12 screenshot: {path}")


def example_caching():
    """Demonstrate caching behavior."""
    print("\n5. Caching demonstration")
    
    import time
    
    # First call - will take screenshot
    start = time.time()
    path1 = capture_screenshot("https://example.com", use_cache=True)
    duration1 = time.time() - start
    print(f"   First call: {duration1:.2f}s - {path1}")
    
    # Second call - should use cache
    start = time.time()
    path2 = capture_screenshot("https://example.com", use_cache=True)
    duration2 = time.time() - start
    print(f"   Cached call: {duration2:.2f}s - {path2}")
    
    # Force fresh screenshot
    start = time.time()
    path3 = capture_screenshot("https://example.com", use_cache=False)
    duration3 = time.time() - start
    print(f"   Fresh call: {duration3:.2f}s - {path3}")


def example_error_handling():
    """Show how to handle errors."""
    print("\n6. Error handling")
    
    from snapwright import BrowserError, TimeoutError
    
    # Invalid URL
    try:
        screenshot("not-a-valid-url")
    except BrowserError as e:
        print(f"   Expected error: {e}")
    
    # Timeout example
    try:
        capture_screenshot(
            "https://example.com",
            wait_for=".non-existent-element",
            wait_timeout=2000
        )
    except TimeoutError as e:
        print(f"   Timeout error: {e}")


if __name__ == "__main__":
    print("=== SnapWright Examples ===\n")
    
    # Run all examples
    example_simple_screenshot()
    example_full_control()
    example_dynamic_content()
    example_mobile_screenshots()
    example_caching()
    example_error_handling()
    
    print("\n✅ All examples completed!")