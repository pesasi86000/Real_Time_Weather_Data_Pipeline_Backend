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
    Thread-safe cache for weather data with TTL support and a maximum size cap.
    When the cache is full, the oldest entry is evicted (LRU-lite: insertion-order eviction).
    """
    
    def __init__(self, ttl_seconds=600, max_size=500):
        self.cache = {}
        self.ttl = ttl_seconds
        self.max_size = max_size
        self.lock = Lock()
        logger.info(f"DataCache initialized with TTL: {ttl_seconds}s, max_size: {max_size}")
    
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
        """Set value in cache with current timestamp; evict oldest entry if at capacity"""
        with self.lock:
            # Evict oldest entry when at capacity (and key is not already present)
            if key not in self.cache and len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                logger.debug(f"Cache eviction (max_size={self.max_size}): removed key {oldest_key}")
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
                'ttl_seconds': self.ttl,
                'max_size': self.max_size
            }


# Global cache instance for weather data
weather_cache = DataCache(ttl_seconds=600)  # 10 minutes cache

# Global cache instance for batch operations
batch_cache = DataCache(ttl_seconds=300)  # 5 minutes cache
