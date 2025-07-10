#!/usr/bin/env python3
"""Data extraction examples using SnapWright."""

from snapwright import browse_and_extract, batch_screenshots
import json


def example_extract_weather_data():
    """Extract weather information from a weather website."""
    print("1. Weather Data Extraction")
    
    # Note: This is a mock example - adjust selectors for real websites
    result = browse_and_extract(
        "https://www.weather.com",
        {
            "current_temp": "[data-testid='TemperatureValue']",
            "condition": "[data-testid='wxPhrase']",
            "humidity": "[data-testid='PercentageValue']",
            "wind_speed": "[data-testid='Wind']",
            "forecast_high": ".forecast-high",
            "forecast_low": ".forecast-low"
        },
        screenshot=True,
        screenshot_path="weather_data.png"
    )
    
    print("   Extracted data:")
    for key, value in result['extracted'].items():
        print(f"   - {key}: {value}")
    
    if result['screenshot']:
        print(f"   Screenshot: {result['screenshot']}")
    
    return result


def example_extract_product_info():
    """Extract product information from an e-commerce site."""
    print("\n2. Product Information Extraction")
    
    # Example for a hypothetical product page
    result = browse_and_extract(
        "https://example.com/product",
        {
            "title": "h1.product-title",
            "price": ".price-now",
            "original_price": ".price-was",
            "rating": ".star-rating",
            "availability": ".availability-status",
            "description": ".product-description",
            "features": "ul.product-features li",  # Will return list
            "images": "img.product-image"  # Will return list of src attributes
        },
        wait_for=".product-loaded",
        wait_timeout=10000
    )
    
    print("   Product details:")
    print(json.dumps(result['extracted'], indent=2))
    
    return result


def example_extract_news_headlines():
    """Extract news headlines from a news website."""
    print("\n3. News Headlines Extraction")
    
    result = browse_and_extract(
        "https://news.ycombinator.com",
        {
            "headlines": ".titleline > a",
            "scores": ".score",
            "comments": ".subline > a:last-child",
            "domains": ".sitestr"
        },
        screenshot=True,
        screenshot_path="news_headlines.png"
    )
    
    # Process the extracted data
    headlines = result['extracted'].get('headlines', [])
    if isinstance(headlines, list):
        print(f"   Found {len(headlines)} headlines:")
        for i, headline in enumerate(headlines[:5]):  # Show first 5
            print(f"   {i+1}. {headline}")
    
    return result


def example_batch_capture():
    """Capture screenshots of multiple websites efficiently."""
    print("\n4. Batch Screenshot Capture")
    
    websites = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://python.org",
        "https://playwright.dev"
    ]
    
    results = batch_screenshots(
        websites,
        output_dir="batch_screenshots",
        full_page=True,
        use_cache=True,
        delay_between=1000,  # 1 second between captures
        name_prefix="site"
    )
    
    print("   Batch results:")
    for url, path in results.items():
        status = "✓" if path else "✗"
        print(f"   {status} {url} -> {path}")
    
    return results


def example_monitor_prices():
    """Example of monitoring prices across multiple sites."""
    print("\n5. Price Monitoring")
    
    # Define sites to monitor
    sites_to_monitor = [
        {
            "name": "Example Store 1",
            "url": "https://example.com/product1",
            "selectors": {
                "name": ".product-name",
                "price": ".current-price",
                "stock": ".stock-status"
            }
        },
        {
            "name": "Example Store 2",
            "url": "https://example.com/product2",
            "selectors": {
                "name": "h1.title",
                "price": "span.price",
                "stock": ".availability"
            }
        }
    ]
    
    monitoring_results = []
    
    for site in sites_to_monitor:
        print(f"   Checking {site['name']}...")
        
        result = browse_and_extract(
            site['url'],
            site['selectors'],
            screenshot=False  # No screenshot for monitoring
        )
        
        if not result['error']:
            monitoring_results.append({
                'store': site['name'],
                'data': result['extracted'],
                'timestamp': result['timestamp']
            })
            
            # Display results
            data = result['extracted']
            print(f"     - Product: {data.get('name', 'N/A')}")
            print(f"     - Price: {data.get('price', 'N/A')}")
            print(f"     - Stock: {data.get('stock', 'N/A')}")
    
    return monitoring_results


def example_extract_with_interaction():
    """Extract data that requires interaction (mock example)."""
    print("\n6. Data Extraction with Wait Conditions")
    
    # This example shows how to wait for dynamic content
    result = browse_and_extract(
        "https://example.com/dynamic",
        {
            "initial_content": ".static-content",
            "dynamic_content": ".ajax-loaded-content",
            "chart_data": ".chart-container",
            "table_rows": "table.data-table tbody tr"
        },
        wait_for=".ajax-loaded-content",  # Wait for AJAX content
        wait_timeout=15000,  # 15 second timeout
        screenshot=True,
        screenshot_path="dynamic_content.png"
    )
    
    print("   Dynamic content extraction:")
    if result['error']:
        print(f"   Error: {result['error']}")
    else:
        for key, value in result['extracted'].items():
            if isinstance(value, list):
                print(f"   - {key}: {len(value)} items")
            else:
                print(f"   - {key}: {value[:50]}..." if value and len(str(value)) > 50 else f"   - {key}: {value}")
    
    return result


if __name__ == "__main__":
    print("=== Data Extraction Examples ===\n")
    
    # Run examples
    example_extract_weather_data()
    example_extract_product_info()
    example_extract_news_headlines()
    example_batch_capture()
    example_monitor_prices()
    example_extract_with_interaction()
    
    print("\n✅ All extraction examples completed!")