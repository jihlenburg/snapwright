"""Smart caching for screenshots."""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from .config import browser_config
from .exceptions import CacheError

logger = logging.getLogger(__name__)


class ScreenshotCache:
    """Manages screenshot caching with metadata."""
    
    def __init__(self):
        self.cache_dir = Path(browser_config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save cache metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
            raise CacheError(f"Failed to save cache metadata: {e}")
    
    def get_cache_key(self, url: str, options: Dict[str, Any] = None) -> str:
        """Generate unique cache key."""
        key_data = {
            'url': url,
            'options': options or {},
            'viewport': f"{browser_config.viewport_width}x{browser_config.viewport_height}"
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_cached_path(self, url: str, options: Dict[str, Any] = None) -> Optional[Path]:
        """Get cached screenshot if valid."""
        if not browser_config.cache_enabled:
            return None
            
        cache_key = self.get_cache_key(url, options)
        
        # Check metadata
        if cache_key in self.metadata:
            entry = self.metadata[cache_key]
            cached_time = datetime.fromisoformat(entry['timestamp'])
            
            # Check if cache is still valid
            if datetime.now() - cached_time < timedelta(hours=browser_config.cache_ttl_hours):
                cache_path = self.cache_dir / entry['filename']
                if cache_path.exists():
                    logger.debug(f"Cache hit for {url}")
                    return cache_path
                else:
                    # Clean up orphaned metadata
                    del self.metadata[cache_key]
                    self._save_metadata()
        
        return None
    
    def save_to_cache(self, url: str, screenshot_path: Path, options: Dict[str, Any] = None) -> Path:
        """Save screenshot to cache."""
        if not browser_config.cache_enabled:
            return screenshot_path
            
        cache_key = self.get_cache_key(url, options)
        cache_filename = f"{cache_key}.png"
        cache_path = self.cache_dir / cache_filename
        
        # Copy to cache
        try:
            import shutil
            shutil.copy2(screenshot_path, cache_path)
            
            # Update metadata
            self.metadata[cache_key] = {
                'url': url,
                'filename': cache_filename,
                'timestamp': datetime.now().isoformat(),
                'options': options or {}
            }
            self._save_metadata()
            
            logger.debug(f"Saved to cache: {url}")
            return cache_path
            
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")
            # Return original path if caching fails
            return screenshot_path
    
    def cleanup_old_cache(self, force: bool = False):
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = []
        
        ttl_multiplier = 1 if force else 2
        max_age = timedelta(hours=browser_config.cache_ttl_hours * ttl_multiplier)
        
        for key, entry in self.metadata.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if now - cached_time > max_age:
                expired_keys.append(key)
                
                # Delete file
                cache_path = self.cache_dir / entry['filename']
                if cache_path.exists():
                    try:
                        cache_path.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete cache file: {e}")
        
        # Remove from metadata
        for key in expired_keys:
            del self.metadata[key]
        
        if expired_keys:
            self._save_metadata()
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear_cache(self):
        """Clear all cache entries."""
        # Delete all cache files
        for cache_file in self.cache_dir.glob("*.png"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete {cache_file}: {e}")
        
        # Clear metadata
        self.metadata.clear()
        self._save_metadata()
        logger.info("Cleared all cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.png"))
        
        return {
            'total_entries': len(self.metadata),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'oldest_entry': min(
                (datetime.fromisoformat(e['timestamp']) for e in self.metadata.values()),
                default=None
            ),
            'newest_entry': max(
                (datetime.fromisoformat(e['timestamp']) for e in self.metadata.values()),
                default=None
            )
        }


# Global cache instance
screenshot_cache = ScreenshotCache()