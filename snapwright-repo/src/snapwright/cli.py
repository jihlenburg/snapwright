#!/usr/bin/env python3
"""Command-line interface for SnapWright."""

import argparse
import sys
from pathlib import Path

from . import capture_screenshot, batch_screenshots, __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Capture website screenshots using Playwright",
        epilog="Examples:\n"
               "  snapwright https://example.com\n"
               "  snapwright https://example.com --output screenshot.png\n"
               "  snapwright --batch urls.txt --output-dir screenshots/",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "url",
        nargs="?",
        help="URL to capture (or use --batch for multiple URLs)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"snapwright {__version__}"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output filename for single URL"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("screenshots"),
        help="Output directory (default: screenshots)"
    )
    
    # Screenshot options
    parser.add_argument(
        "--full-page",
        action="store_true",
        default=True,
        help="Capture full page (default: True)"
    )
    
    parser.add_argument(
        "--viewport",
        action="store_false",
        dest="full_page",
        help="Capture viewport only"
    )
    
    parser.add_argument(
        "--selector",
        help="CSS selector for specific element"
    )
    
    parser.add_argument(
        "--wait-for",
        help="CSS selector to wait for before capture"
    )
    
    parser.add_argument(
        "--wait-timeout",
        type=int,
        default=5000,
        help="Timeout for wait-for selector (ms, default: 5000)"
    )
    
    parser.add_argument(
        "--extra-wait",
        type=int,
        default=0,
        help="Additional wait time after page load (ms)"
    )
    
    # Batch options
    parser.add_argument(
        "--batch",
        type=Path,
        help="File containing URLs (one per line)"
    )
    
    parser.add_argument(
        "--delay",
        type=int,
        default=1000,
        help="Delay between batch captures (ms, default: 1000)"
    )
    
    # Cache options
    parser.add_argument(
        "--no-cache",
        action="store_false",
        dest="use_cache",
        help="Disable cache"
    )
    
    # Device options
    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Use mobile viewport"
    )
    
    parser.add_argument(
        "--device",
        choices=["iPhone 12", "iPad", "Pixel 5"],
        help="Specific device to emulate"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.batch:
        parser.error("Either URL or --batch is required")
    
    if args.url and args.batch:
        parser.error("Cannot specify both URL and --batch")
    
    try:
        if args.batch:
            # Batch mode
            if not args.batch.exists():
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                sys.exit(1)
            
            # Read URLs from file
            urls = []
            with open(args.batch) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        urls.append(line)
            
            if not urls:
                print("Error: No URLs found in batch file", file=sys.stderr)
                sys.exit(1)
            
            print(f"Processing {len(urls)} URLs...")
            
            results = batch_screenshots(
                urls,
                output_dir=args.output_dir,
                full_page=args.full_page,
                use_cache=args.use_cache,
                delay_between=args.delay
            )
            
            # Print results
            success_count = sum(1 for path in results.values() if path)
            print(f"\nCompleted: {success_count}/{len(urls)} successful")
            
            for url, path in results.items():
                status = "✓" if path else "✗"
                print(f"{status} {url}")
            
        else:
            # Single URL mode
            print(f"Capturing: {args.url}")
            
            path = capture_screenshot(
                args.url,
                output_path=args.output,
                full_page=args.full_page,
                selector=args.selector,
                wait_for=args.wait_for,
                wait_timeout=args.wait_timeout,
                use_cache=args.use_cache,
                extra_wait=args.extra_wait,
                mobile=args.mobile,
                device_name=args.device
            )
            
            if path:
                print(f"Screenshot saved to: {path}")
            else:
                print("Error: Failed to capture screenshot", file=sys.stderr)
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nCancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()