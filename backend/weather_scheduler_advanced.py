"""
Advanced Weather Scheduler Example
Demonstrates advanced scheduling patterns and configurations
"""

import time
import signal
import sys
import schedule
from datetime import datetime
from fetch_weather_csv import fetch_and_save_weather
from helpers import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# ADVANCED CONFIGURATION EXAMPLES
# ============================================================================

class SchedulerConfig:
    """Configuration class for flexible scheduler setup"""
    
    def __init__(self):
        # City groups for different schedules
        self.priority_cities = ['London', 'New York', 'Tokyo']  # High priority - frequent updates
        self.standard_cities = ['Paris', 'Sydney', 'Dubai']     # Standard frequency
        self.low_priority_cities = ['Mumbai', 'Singapore']      # Less frequent updates
        
        # Units
        self.temp_units = 'metric'


config = SchedulerConfig()


# ============================================================================
# EXAMPLE 1: Different Intervals for Different City Groups
# ============================================================================

def collect_priority_cities():
    """Collect high-priority cities every 5 minutes"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] [PRIORITY] Fetching high-priority cities...")
    
    success, message = fetch_and_save_weather(config.priority_cities, config.temp_units)
    if success:
        logger.info(f"[{timestamp}] [PRIORITY] ✓ {message}")
    else:
        logger.error(f"[{timestamp}] [PRIORITY] ✗ {message}")


def collect_standard_cities():
    """Collect standard cities every 10 minutes"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] [STANDARD] Fetching standard cities...")
    
    success, message = fetch_and_save_weather(config.standard_cities, config.temp_units)
    if success:
        logger.info(f"[{timestamp}] [STANDARD] ✓ {message}")
    else:
        logger.error(f"[{timestamp}] [STANDARD] ✗ {message}")


def collect_low_priority_cities():
    """Collect low-priority cities every 30 minutes"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] [LOW-PRIORITY] Fetching low-priority cities...")
    
    success, message = fetch_and_save_weather(config.low_priority_cities, config.temp_units)
    if success:
        logger.info(f"[{timestamp}] [LOW-PRIORITY] ✓ {message}")
    else:
        logger.error(f"[{timestamp}] [LOW-PRIORITY] ✗ {message}")


# ============================================================================
# EXAMPLE 2: Schedule at Specific Times
# ============================================================================

def collect_at_specific_times():
    """
    Alternative approach: Schedule at specific times of day
    Useful for daily reports or specific analysis times
    
    Uncomment in start_advanced_scheduler() to use
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] Scheduled time collection triggered")
    
    all_cities = config.priority_cities + config.standard_cities + config.low_priority_cities
    success, message = fetch_and_save_weather(all_cities, config.temp_units)
    if success:
        logger.info(f"[{timestamp}] ✓ {message}")
    else:
        logger.error(f"[{timestamp}] ✗ {message}")


# ============================================================================
# EXAMPLE 3: Conditional Scheduling (Advanced)
# ============================================================================

def collect_all_cities_on_demand(force=False):
    """
    Collect all cities with optional force flag
    Can be triggered manually or based on conditions
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trigger = "FORCED" if force else "SCHEDULED"
    logger.info(f"[{timestamp}] [{trigger}] Collecting all cities...")
    
    all_cities = config.priority_cities + config.standard_cities + config.low_priority_cities
    success, message = fetch_and_save_weather(all_cities, config.temp_units)
    if success:
        logger.info(f"[{timestamp}] [{trigger}] ✓ {message}")
    else:
        logger.error(f"[{timestamp}] [{trigger}] ✗ {message}")


# ============================================================================
# ADVANCED SCHEDULER START FUNCTION
# ============================================================================

def start_advanced_scheduler():
    """
    Advanced scheduler with multiple job types and intervals
    """
    logger.info("=" * 70)
    logger.info("ADVANCED WEATHER SCHEDULER STARTED")
    logger.info("=" * 70)
    
    # Schedule different city groups at different intervals
    logger.info("Priority cities: Every 5 minutes")
    schedule.every(5).minutes.do(collect_priority_cities)
    
    logger.info("Standard cities: Every 10 minutes")
    schedule.every(10).minutes.do(collect_standard_cities)
    
    logger.info("Low-priority cities: Every 30 minutes")
    schedule.every(30).minutes.do(collect_low_priority_cities)
    
    # OPTIONAL: Schedule at specific times (example for daily reports)
    # logger.info("Daily report: Every day at 09:00")
    # schedule.every().day.at("09:00").do(collect_at_specific_times)
    
    # OPTIONAL: Schedule at specific days/times
    # logger.info("Weekly report: Every Monday at 09:00")
    # schedule.every().monday.at("09:00").do(collect_at_specific_times)
    
    logger.info("=" * 70)
    
    # Run immediately if desired
    logger.info("Running initial collection for all groups...")
    collect_priority_cities()
    
    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Advanced scheduler stopped by user")
        schedule.clear()
        sys.exit(0)


# ============================================================================
# EXAMPLE 4: Load Cities from Configuration File
# ============================================================================

def load_cities_from_config(config_file='cities_config.txt'):
    """
    Load cities from an external configuration file
    Format: One city per line, or comma-separated groups
    
    Example cities_config.txt:
    ```
    [PRIORITY]
    London
    New York
    Tokyo
    
    [STANDARD]
    Paris
    Sydney
    Dubai
    
    [LOW_PRIORITY]
    Mumbai
    Singapore
    ```
    """
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            logger.info(f"Loaded cities from {config_file}")
            return content
    except FileNotFoundError:
        logger.warning(f"Config file {config_file} not found. Using default cities.")
        return None


# ============================================================================
# EXAMPLE 5: Scheduler with Error Retry Logic
# ============================================================================

class RobustScheduler:
    """Scheduler with retry logic for failed collections"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay_seconds = 30
        self.failed_jobs = []
    
    def collect_with_retry(self, cities, attempt=1):
        """Collect weather with automatic retry on failure"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            success, message = fetch_and_save_weather(cities, 'metric')
            
            if not success and attempt < self.max_retries:
                logger.warning(f"[{timestamp}] Attempt {attempt} failed. Retrying in {self.retry_delay_seconds}s...")
                time.sleep(self.retry_delay_seconds)
                self.collect_with_retry(cities, attempt + 1)
            elif success:
                logger.info(f"[{timestamp}] ✓ Collection successful on attempt {attempt}")
                self.failed_jobs.clear()
            else:
                logger.error(f"[{timestamp}] ✗ Failed after {self.max_retries} attempts")
                self.failed_jobs.append((timestamp, cities))
                
        except Exception as e:
            logger.error(f"[{timestamp}] Exception: {str(e)}")
            if attempt < self.max_retries:
                time.sleep(self.retry_delay_seconds)
                self.collect_with_retry(cities, attempt + 1)
    
    def get_failed_jobs(self):
        """Get list of jobs that failed all retries"""
        return self.failed_jobs


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ADVANCED SCHEDULER EXAMPLES")
    print("=" * 70)
    print()
    print("This file demonstrates advanced scheduling patterns:")
    print()
    print("1. Different intervals for different city groups (RECOMMENDED)")
    print("   - Priority cities: every 5 minutes")
    print("   - Standard cities: every 10 minutes")
    print("   - Low-priority: every 30 minutes")
    print()
    print("2. Scheduling at specific times of day")
    print("   - Example: 09:00 AM daily")
    print("   - Example: Every Monday at 09:00")
    print()
    print("3. Conditional scheduling based on rules")
    print()
    print("4. Loading configuration from files")
    print()
    print("5. Retry logic for failed collections")
    print()
    print("=" * 70)
    print()
    print("To use the advanced scheduler:")
    print()
    print("1. Uncomment the desired functions in start_advanced_scheduler()")
    print("2. Modify cities in SchedulerConfig")
    print("3. Run: python weather_scheduler_advanced.py")
    print()
    print("=" * 70)
    print()
    
    # Uncomment to run the advanced scheduler:
    # start_advanced_scheduler()
