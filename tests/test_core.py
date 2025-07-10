"""Tests for core functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from snapwright import (
    screenshot,
    capture_screenshot,
    browse_and_extract,
    batch_screenshots
)
from snapwright.exceptions import (
    BrowserError,
    TimeoutError,
    ElementNotFoundError
)


class TestScreenshot:
    """Test basic screenshot functionality."""
    
    def test_simple_screenshot(self, tmp_path):
        """Test simple screenshot function."""
        with patch('snapwright.core.capture_screenshot') as mock_capture:
            expected_path = tmp_path / "screenshot.png"
            mock_capture.return_value = expected_path
            
            result = screenshot("https://example.com")
            
            assert result == expected_path
            mock_capture.assert_called_once_with("https://example.com", output_path=None)
    
    def test_screenshot_with_filename(self, tmp_path):
        """Test screenshot with custom filename."""
        with patch('snapwright.core.capture_screenshot') as mock_capture:
            expected_path = tmp_path / "custom.png"
            mock_capture.return_value = expected_path
            
            result = screenshot("https://example.com", "custom.png")
            
            assert result == expected_path
            mock_capture.assert_called_once()
            
            # Check that output_path was set
            call_args = mock_capture.call_args
            assert "output_path" in call_args.kwargs or len(call_args.args) > 1


class TestCaptureScreenshot:
    """Test advanced screenshot capture."""
    
    @patch('snapwright.core.browser_manager')
    @patch('snapwright.core.screenshot_cache')
    def test_capture_with_cache_hit(self, mock_cache, mock_browser, tmp_path):
        """Test screenshot with cache hit."""
        cached_path = tmp_path / "cached.png"
        cached_path.touch()
        
        mock_cache.get_cached_path.return_value = cached_path
        
        result = capture_screenshot("https://example.com", use_cache=True)
        
        assert result == cached_path
        mock_browser.get_context.assert_not_called()
    
    @patch('snapwright.core.browser_manager')
    @patch('snapwright.core.screenshot_cache')
    def test_capture_with_cache_miss(self, mock_cache, mock_browser, tmp_path):
        """Test screenshot with cache miss."""
        mock_cache.get_cached_path.return_value = None
        
        # Mock page and context
        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        output_path = tmp_path / "new.png"
        result = capture_screenshot(
            "https://example.com",
            output_path=output_path,
            use_cache=True
        )
        
        # Verify browser interaction
        mock_browser.get_context.assert_called_once()
        mock_page.goto.assert_called_once()
        mock_page.screenshot.assert_called_once()
        mock_page.close.assert_called_once()
    
    @patch('snapwright.core.browser_manager')
    def test_capture_with_selector(self, mock_browser):
        """Test element screenshot."""
        mock_element = Mock()
        mock_page = Mock()
        mock_page.query_selector.return_value = mock_element
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        capture_screenshot("https://example.com", selector=".test-element")
        
        mock_page.query_selector.assert_called_with(".test-element")
        mock_element.screenshot.assert_called_once()
    
    @patch('snapwright.core.browser_manager')
    def test_capture_with_wait_for(self, mock_browser):
        """Test waiting for element."""
        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        capture_screenshot(
            "https://example.com",
            wait_for=".dynamic-content",
            wait_timeout=5000
        )
        
        mock_page.wait_for_selector.assert_called_with(".dynamic-content", timeout=5000)


class TestBrowseAndExtract:
    """Test browse and extract functionality."""
    
    @patch('snapwright.core.browser_manager')
    def test_extract_single_elements(self, mock_browser):
        """Test extracting single elements."""
        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        # Mock elements
        mock_title = Mock()
        mock_title.text_content.return_value = "Test Title"
        mock_content = Mock()
        mock_content.text_content.return_value = "Test Content"
        
        mock_page.query_selector_all.side_effect = [
            [mock_title],  # Single element for title
            [mock_content]  # Single element for content
        ]
        
        result = browse_and_extract(
            "https://example.com",
            {
                "title": "h1",
                "content": ".content"
            }
        )
        
        assert result['extracted']['title'] == "Test Title"
        assert result['extracted']['content'] == "Test Content"
        assert result['error'] is None
    
    @patch('snapwright.core.browser_manager')
    def test_extract_multiple_elements(self, mock_browser):
        """Test extracting multiple elements."""
        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        # Mock multiple elements
        mock_items = [Mock(), Mock(), Mock()]
        for i, item in enumerate(mock_items):
            item.text_content.return_value = f"Item {i+1}"
        
        mock_page.query_selector_all.return_value = mock_items
        
        result = browse_and_extract(
            "https://example.com",
            {"items": "li"}
        )
        
        assert len(result['extracted']['items']) == 3
        assert result['extracted']['items'] == ["Item 1", "Item 2", "Item 3"]


class TestBatchScreenshots:
    """Test batch screenshot functionality."""
    
    @patch('snapwright.core.capture_screenshot')
    def test_batch_processing(self, mock_capture, tmp_path):
        """Test processing multiple URLs."""
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        
        # Mock successful captures
        mock_capture.side_effect = [
            tmp_path / "shot1.png",
            tmp_path / "shot2.png",
            tmp_path / "shot3.png"
        ]
        
        results = batch_screenshots(urls)
        
        assert len(results) == 3
        assert all(path is not None for path in results.values())
        assert mock_capture.call_count == 3
    
    @patch('snapwright.core.capture_screenshot')
    @patch('snapwright.core.time.sleep')
    def test_batch_with_delay(self, mock_sleep, mock_capture, tmp_path):
        """Test batch processing with delay."""
        urls = ["https://example1.com", "https://example2.com"]
        
        mock_capture.side_effect = [tmp_path / "shot1.png", tmp_path / "shot2.png"]
        
        batch_screenshots(urls, delay_between=2000)
        
        # Should sleep once (between the two captures)
        mock_sleep.assert_called_once_with(2.0)


class TestErrorHandling:
    """Test error handling."""
    
    @patch('snapwright.core.browser_manager')
    def test_navigation_error(self, mock_browser):
        """Test navigation error handling."""
        from playwright.sync_api import Error as PlaywrightError
        
        mock_page = Mock()
        mock_page.goto.side_effect = PlaywrightError("Navigation failed")
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        with pytest.raises(NavigationError):
            capture_screenshot("https://invalid-url.com")
    
    @patch('snapwright.core.browser_manager')
    def test_element_not_found(self, mock_browser):
        """Test element not found error."""
        mock_page = Mock()
        mock_page.query_selector.return_value = None
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        with pytest.raises(ElementNotFoundError):
            capture_screenshot("https://example.com", selector=".non-existent")
    
    @patch('snapwright.core.browser_manager')
    def test_timeout_error(self, mock_browser):
        """Test timeout error."""
        from playwright.sync_api import Error as PlaywrightError
        
        mock_page = Mock()
        mock_page.wait_for_selector.side_effect = PlaywrightError("Timeout")
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser.get_context.return_value = mock_context
        
        with pytest.raises(TimeoutError):
            capture_screenshot(
                "https://example.com",
                wait_for=".slow-element",
                wait_timeout=1000
            )