"""
Resilience Module
Implements retry logic, rate limiting, and circuit breaker patterns
for improved reliability and fault tolerance
"""

import time
from functools import wraps
from threading import Lock
from datetime import datetime, timedelta
from collections import deque
from helpers import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """
    Token bucket based rate limiter for API requests
    Prevents overwhelming external APIs and respects rate limits
    """
    
    def __init__(self, max_requests=60, time_window=60):
        """
        Initialize rate limiter
        
        Args:
            max_requests (int): Maximum requests allowed
            time_window (int): Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = Lock()
        logger.info(f"RateLimiter initialized: {max_requests} requests per {time_window}s")
    
    def is_allowed(self):
        """
        Check if request is allowed within rate limit
        
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        with self.lock:
            now = time.time()
            
            # Remove old requests outside the time window
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            
            # Check if we've hit the limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_retry_after(self):
        """
        Get seconds to wait before next request is allowed
        
        Returns:
            float: Seconds to wait
        """
        with self.lock:
            if not self.requests:
                return 0
            
            oldest_request = self.requests[0]
            retry_after = self.time_window - (time.time() - oldest_request)
            return max(0, retry_after)
    
    def reset(self):
        """Reset the rate limiter"""
        with self.lock:
            self.requests.clear()
            logger.info("RateLimiter reset")

    def get_request_count(self):
        """Return the number of requests in the current time window (thread-safe)"""
        with self.lock:
            now = time.time()
            return sum(1 for ts in self.requests if ts >= now - self.time_window)


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures
    Tracks failures and temporarily stops requests if error rate is too high
    """
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold (int): Number of failures before opening circuit
            recovery_timeout (int): Seconds before attempting to recover
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = Lock()
        logger.info(f"CircuitBreaker initialized: threshold={failure_threshold}, timeout={recovery_timeout}s")
    
    def record_success(self):
        """Record a successful request"""
        with self.lock:
            self.failure_count = 0
            self.success_count += 1
            
            if self.state == 'HALF_OPEN' and self.success_count >= 2:
                logger.info("CircuitBreaker: Recovered - switching to CLOSED")
                self.state = 'CLOSED'
                self.success_count = 0
    
    def record_failure(self):
        """Record a failed request"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            logger.warning(f"CircuitBreaker: Failure recorded ({self.failure_count}/{self.failure_threshold})")
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error("CircuitBreaker: Threshold exceeded - switching to OPEN")
    
    def can_attempt(self):
        """
        Check if a request can be attempted
        
        Returns:
            bool: True if request can be attempted
        """
        with self.lock:
            if self.state == 'CLOSED':
                return True
            
            if self.state == 'OPEN':
                # Check if recovery timeout has elapsed
                if self.last_failure_time and time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info("CircuitBreaker: Recovery timeout elapsed - switching to HALF_OPEN")
                    self.state = 'HALF_OPEN'
                    self.success_count = 0
                    return True
                return False
            
            # HALF_OPEN state: allow limited requests
            return True
    
    def get_state(self):
        """Get current circuit breaker state"""
        with self.lock:
            return {
                'state': self.state,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure': self.last_failure_time
            }
    
    def reset(self):
        """Reset the circuit breaker"""
        with self.lock:
            self.failure_count = 0
            self.success_count = 0
            self.state = 'CLOSED'
            self.last_failure_time = None
            logger.info("CircuitBreaker reset")


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff
    """
    
    def __init__(self, max_attempts=3, base_delay=1, max_delay=60, backoff_factor=2):
        """
        Initialize retry policy
        
        Args:
            max_attempts (int): Maximum number of retry attempts
            base_delay (float): Initial delay in seconds
            max_delay (float): Maximum delay in seconds
            backoff_factor (float): Exponential backoff multiplier
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        logger.info(f"RetryPolicy initialized: max_attempts={max_attempts}, base_delay={base_delay}s")
    
    def get_retry_delay(self, attempt):
        """
        Calculate delay for given attempt number
        
        Args:
            attempt (int): Attempt number (0-indexed)
            
        Returns:
            float: Delay in seconds
        """
        delay = self.base_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
    
    def should_retry(self, attempt, error_type):
        """
        Determine if request should be retried
        
        Args:
            attempt (int): Attempt number (0-indexed)
            error_type (str): Type of error
            
        Returns:
            bool: True if request should be retried
        """
        if attempt >= self.max_attempts - 1:
            return False
        
        # Don't retry on client errors (4xx)
        if error_type and 'client' in error_type.lower():
            return False
        
        # Retry on server errors (5xx) and timeouts
        if error_type and ('server' in error_type.lower() or 'timeout' in error_type.lower()):
            return True
        
        return True


def retry_with_backoff(max_attempts=3, base_delay=1, backoff_factor=2, retryable_exceptions=None):
    """
    Decorator to add retry logic with exponential backoff
    
    Args:
        max_attempts (int): Maximum retry attempts
        base_delay (float): Initial delay in seconds
        backoff_factor (float): Exponential backoff multiplier
        retryable_exceptions (tuple): Exceptions that should trigger retry
        
    Returns:
        function: Decorated function
        
    Example:
        @retry_with_backoff(max_attempts=3, base_delay=1)
        def fetch_data():
            return requests.get(...)
    """
    if retryable_exceptions is None:
        retryable_exceptions = (Exception,)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Max retry attempts ({max_attempts}) reached for {func.__name__}")
                        raise
                    
                    delay = base_delay * (backoff_factor ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
            
            return None
        
        return wrapper
    
    return decorator


def rate_limit_check(limiter):
    """
    Decorator to enforce rate limiting
    
    Args:
        limiter (RateLimiter): RateLimiter instance
        
    Returns:
        function: Decorated function
        
    Raises:
        RuntimeError: If rate limit exceeded
        
    Example:
        limiter = RateLimiter(max_requests=60, time_window=60)
        
        @rate_limit_check(limiter)
        def call_api():
            return requests.get(...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.is_allowed():
                retry_after = limiter.get_retry_after()
                error_msg = f"Rate limit exceeded. Retry after {retry_after:.1f} seconds"
                logger.warning(error_msg)
                raise RuntimeError(error_msg)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def circuit_breaker_protected(breaker):
    """
    Decorator to protect function with circuit breaker
    
    Args:
        breaker (CircuitBreaker): CircuitBreaker instance
        
    Returns:
        function: Decorated function
        
    Example:
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        
        @circuit_breaker_protected(breaker)
        def call_api():
            return requests.get(...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not breaker.can_attempt():
                state = breaker.get_state()
                error_msg = f"Circuit breaker is {state['state']}. Cannot make request."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
        
        return wrapper
    
    return decorator


# Global instances
rate_limiter = RateLimiter(max_requests=60, time_window=60)  # 60 requests per minute
api_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
retry_policy = RetryPolicy(max_attempts=3, base_delay=1, max_delay=60)
