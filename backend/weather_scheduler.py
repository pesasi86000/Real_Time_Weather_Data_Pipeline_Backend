"""
Weather Data Scheduler
Schedules periodic weather data collection and saves to CSV
Perfect for continuous background data collection
"""

import time
import signal
import sys
import schedule
from datetime import datetime
from fetch_weather_csv import fetch_and_save_weather
from helpers import setup_logger

# Setup logging
logger = setup_logger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# List of cities to monitor
CITIES_TO_MONITOR = [
    'London',
    'New York',
    'Tokyo',
    'Paris',
    'Sydney',
    'Dubai',
    'Singapore',
    'Mumbai'
]

# Units for temperature ('metric' = Celsius, 'imperial' = Fahrenheit)
TEMPERATURE_UNITS = 'metric'

# Collection interval in minutes (how often to fetch weather)
COLLECTION_INTERVAL_MINUTES = 5


# ============================================================================
# SCHEDULER FUNCTIONS
# ============================================================================

def collect_weather_data():
    """
    Scheduled job: Fetches weather data and saves to CSV
    Called at regular intervals defined by COLLECTION_INTERVAL_MINUTES
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] Starting scheduled weather data collection...")
    
    try:
        success, message = fetch_and_save_weather(CITIES_TO_MONITOR, TEMPERATURE_UNITS)
        
        if success:
            logger.info(f"[{timestamp}] ✓ {message}")
        else:
            logger.error(f"[{timestamp}] ✗ {message}")
            
    except Exception as e:
        logger.error(f"[{timestamp}] ✗ Error during weather collection: {str(e)}")
        logger.exception("Full traceback:")


def start_scheduler():
    """
    Initialize and start the scheduler
    Configures the schedule and starts the event loop
    """
    logger.info("=" * 70)
    logger.info("WEATHER DATA SCHEDULER STARTED")
    logger.info("=" * 70)
    logger.info(f"Collection interval: Every {COLLECTION_INTERVAL_MINUTES} minute(s)")
    logger.info(f"Cities to monitor: {', '.join(CITIES_TO_MONITOR)}")
    logger.info(f"Temperature units: {TEMPERATURE_UNITS}")
    logger.info(f"First collection will run in {COLLECTION_INTERVAL_MINUTES} minute(s)...")
    logger.info("=" * 70)
    
    # Schedule the job to run every N minutes
    schedule.every(COLLECTION_INTERVAL_MINUTES).minutes.do(collect_weather_data)
    
    # Also run immediately on startup (optional - comment out if not desired)
    logger.info("Running initial weather collection...")
    collect_weather_data()
    
    # Keep the scheduler running
    try:
        while True:
            # Check if any jobs should run
            schedule.run_pending()
            
            # Sleep for 1 second before checking again
            # This keeps the scheduler responsive while not consuming CPU
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user (Ctrl+C)")
        stop_scheduler()


def stop_scheduler():
    """
    Gracefully stop the scheduler
    """
    logger.info("=" * 70)
    logger.info("WEATHER DATA SCHEDULER STOPPED")
    logger.info("=" * 70)
    schedule.clear()
    sys.exit(0)


# ============================================================================
# SIGNAL HANDLERS (for graceful shutdown)
# ============================================================================

def handle_sigterm(signum, frame):
    """Handle SIGTERM signal (for proper process termination)"""
    logger.warning("SIGTERM signal received")
    stop_scheduler()


def handle_sigint(signum, frame):
    """Handle SIGINT signal (Ctrl+C)"""
    logger.warning("SIGINT signal received (Ctrl+C)")
    stop_scheduler()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigint)
    
    logger.info("Initializing weather scheduler...")
    
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Fatal error in scheduler: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)
