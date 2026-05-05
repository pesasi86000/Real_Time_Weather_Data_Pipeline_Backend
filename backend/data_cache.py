"""
Data Cache Module
Implements in-memory caching for weather data with TTL (Time-To-Live)
"""

import time
from threading import Lock
from datetime import datetime, timedelta
from helpers import setup_logger

logger = setup_logger(__name__)


class DataCache:
    """
    Thread-safe cache for weather data with TTL support
    """
    
    def __init__(self, ttl_seconds=600):  # Default 10 minutes
        self.cache = {}
        self.ttl = ttl_seconds
        self.lock = Lock()
        logger.info(f"DataCache initialized with TTL: {ttl_seconds}s")
    
    def get(self, key):
        """Get value from cache if not expired"""
        with self.lock:
            if key not in self.cache:
                return None
            
            value, timestamp = self.cache[key]
            
            # Check if expired
            if time.time() - timestamp > self.ttl:
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return value
    
    def set(self, key, value):
        """Set value in cache with current timestamp"""
        with self.lock:
            self.cache[key] = (value, time.time())
            logger.debug(f"Cache set for key: {key}")
    
    def delete(self, key):
        """Delete value from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def get_stats(self):
        """Get cache statistics"""
        with self.lock:
            active_items = sum(1 for _, (_, ts) in self.cache.items() 
                              if time.time() - ts <= self.ttl)
            return {
                'total_items': len(self.cache),
                'active_items': active_items,
                'expired_items': len(self.cache) - active_items,
                'ttl_seconds': self.ttl
            }


# Global cache instance for weather data
weather_cache = DataCache(ttl_seconds=600)  # 10 minutes cache

# Global cache instance for batch operations
batch_cache = DataCache(ttl_seconds=300)  # 5 minutes cache
