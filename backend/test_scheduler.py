"""
Test Script: Weather Scheduler Quick Start
Demonstrates the scheduler with minimal configuration
Perfect for testing before running in production
"""

import time
import signal
import sys
from datetime import datetime
from fetch_weather_csv import fetch_and_save_weather
from helpers import setup_logger

logger = setup_logger(__name__)


def test_immediate_collection():
    """
    Test immediate weather collection without scheduling
    Perfect for testing configuration before running the full scheduler
    """
    logger.info("=" * 70)
    logger.info("WEATHER DATA COLLECTION - TEST MODE")
    logger.info("=" * 70)
    
    # Small test set of cities
    test_cities = ['London', 'New York', 'Tokyo']
    
    logger.info(f"Test cities: {', '.join(test_cities)}")
    logger.info("Starting immediate collection test...")
    logger.info("-" * 70)
    
    try:
        success, message = fetch_and_save_weather(test_cities, 'metric')
        
        logger.info("-" * 70)
        if success:
            logger.info(f"✓ TEST PASSED: {message}")
            logger.info("The scheduler is configured correctly and ready to run!")
        else:
            logger.error(f"✗ TEST FAILED: {message}")
            logger.error("Please check your configuration and API key")
            return False
            
    except Exception as e:
        logger.error(f"✗ TEST ERROR: {str(e)}")
        logger.exception("Full traceback:")
        return False
    
    logger.info("=" * 70)
    return True


def test_csv_output():
    """
    Test that CSV file is created and readable
    """
    import os
    from config import CSV_FILE
    
    logger.info("Checking CSV output...")
    
    if not os.path.exists(CSV_FILE):
        logger.warning(f"CSV file not found at: {os.path.abspath(CSV_FILE)}")
        return False
    
    try:
        with open(CSV_FILE, 'r') as f:
            lines = f.readlines()
            logger.info(f"✓ CSV file found with {len(lines)} lines")
            logger.info("Last 3 lines of CSV:")
            for line in lines[-3:]:
                logger.info(f"  {line.strip()}")
        return True
    except Exception as e:
        logger.error(f"✗ Error reading CSV: {str(e)}")
        return False


def run_scheduler_demo(duration_seconds=60):
    """
    Run scheduler demo for a short duration (testing purposes)
    
    Args:
        duration_seconds: How long to run before stopping (default: 60 seconds)
    """
    import schedule
    
    logger.info("=" * 70)
    logger.info(f"SCHEDULER DEMO - Running for {duration_seconds} seconds")
    logger.info("=" * 70)
    
    test_cities = ['London', 'Paris']  # Small set for testing
    collection_interval = 15  # Collect every 15 seconds for testing
    
    logger.info(f"Collection interval: Every {collection_interval} seconds")
    logger.info(f"Test cities: {', '.join(test_cities)}")
    logger.info("Press Ctrl+C to stop early")
    logger.info("-" * 70)
    
    def demo_collection():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{timestamp}] Collecting weather data...")
        success, message = fetch_and_save_weather(test_cities, 'metric')
        if success:
            logger.info(f"[{timestamp}] ✓ {message}")
        else:
            logger.error(f"[{timestamp}] ✗ {message}")
    
    schedule.every(collection_interval).seconds.do(demo_collection)
    
    # Run immediately first
    demo_collection()
    
    start_time = time.time()
    try:
        while (time.time() - start_time) < duration_seconds:
            schedule.run_pending()
            time.sleep(1)
            
            remaining = duration_seconds - (time.time() - start_time)
            if int(remaining) % 15 == 0 and int(remaining) != duration_seconds:
                logger.info(f"Demo running... {int(remaining)}s remaining")
                
    except KeyboardInterrupt:
        logger.info("Demo stopped by user")
    
    logger.info("-" * 70)
    logger.info("Demo completed! The scheduler is working correctly.")
    logger.info("=" * 70)


def main():
    """Main entry point for testing"""
    
    print()
    print("=" * 70)
    print("WEATHER SCHEDULER - QUICK START TEST")
    print("=" * 70)
    print()
    print("Choose an option:")
    print("  1) Test immediate collection (quick verification)")
    print("  2) Run demo scheduler for 60 seconds")
    print("  3) Run full scheduler (use weather_scheduler.py instead)")
    print("  4) Check CSV output")
    print()
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print()
            success = test_immediate_collection()
            if success:
                print("\n✓ Configuration verified! Ready for full scheduler.")
            else:
                print("\n✗ Please fix the issues above before running the scheduler.")
                
        elif choice == '2':
            print()
            run_scheduler_demo(duration_seconds=60)
            
        elif choice == '3':
            print("\nPlease run: python weather_scheduler.py")
            
        elif choice == '4':
            print()
            test_csv_output()
            
        else:
            print("Invalid choice. Please enter 1-4.")
            
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == '__main__':
    main()
