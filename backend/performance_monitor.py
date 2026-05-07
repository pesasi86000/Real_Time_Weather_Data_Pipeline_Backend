"""
Performance Monitoring Module
Tracks API performance metrics and system health
"""

import time
from collections import defaultdict, deque
from threading import Lock
from datetime import datetime, timedelta
from helpers import setup_logger

logger = setup_logger(__name__)


class PerformanceMonitor:
    """
    Monitors API performance and system health metrics
    """
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.request_times = deque(maxlen=window_size)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
        self.lock = Lock()
        logger.info(f"PerformanceMonitor initialized with window size: {window_size}")
    
    def record_request(self, endpoint, duration, success=True, error_type=None):
        """Record a request metric"""
        with self.lock:
            self.request_times.append(duration)
            
            stats = self.endpoint_stats[endpoint]
            stats['count'] += 1
            stats['total_time'] += duration
            
            if not success:
                stats['errors'] += 1
                if error_type:
                    self.error_counts[error_type] += 1
            
            logger.debug(f"Recorded: {endpoint} - {duration:.3f}s - {'success' if success else 'error'}")
    
    def _get_stats_unlocked(self):
        """Internal: compute stats without acquiring the lock (caller must hold it)."""
        if not self.request_times:
            return {
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'total_requests': 0,
                'error_summary': {}
            }

        times = list(self.request_times)
        return {
            'avg_response_time': sum(times) / len(times),
            'min_response_time': min(times),
            'max_response_time': max(times),
            'total_requests': len(times),
            'error_summary': dict(self.error_counts),
            'endpoint_stats': {k: {
                'count': v['count'],
                'avg_time': v['total_time'] / v['count'] if v['count'] > 0 else 0,
                'error_rate': (v['errors'] / v['count'] * 100) if v['count'] > 0 else 0
            } for k, v in self.endpoint_stats.items()}
        }

    def get_stats(self):
        """Get aggregated performance statistics"""
        with self.lock:
            return self._get_stats_unlocked()

    def get_health_status(self):
        """Get overall health status"""
        with self.lock:
            stats = self._get_stats_unlocked()

            if stats['total_requests'] == 0:
                return 'UNKNOWN'

            error_rate = (sum(self.error_counts.values()) / stats['total_requests']) * 100
            avg_response_time = stats['avg_response_time']

            if error_rate > 10 or avg_response_time > 5:
                return 'DEGRADED'
            elif error_rate > 5 or avg_response_time > 2:
                return 'WARNING'
            else:
                return 'HEALTHY'
    
    def reset_stats(self):
        """Reset all statistics"""
        with self.lock:
            self.request_times.clear()
            self.error_counts.clear()
            self.endpoint_stats.clear()
            logger.info("Performance statistics reset")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
