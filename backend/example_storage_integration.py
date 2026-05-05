"""
Storage Integration Examples
Demonstrates how to use the data_storage module with existing weather code.

These are beginner-friendly examples showing common use cases.
Copy and adapt these patterns to your own code.
"""

# ============================================================================
# EXAMPLE 1: Simple Weather Data Collection and Storage
# ============================================================================

def example_collect_and_store():
    """
    Collect weather data from API and save it to storage.
    Best for: Learning how to save single records.
    """
    from data_storage import initialize_storage, save_weather_data
    from weather_service import fetch_weather_data
    
    # Initialize storage once
    initialize_storage()
    
    # Fetch weather data
    success, weather_data = fetch_weather_data('London', 'metric')
    
    if success:
        # Save to storage (CSV or SQLite based on config)
        save_success, save_message = save_weather_data(weather_data)
        print(save_message)
    else:
        print(f"Error fetching weather: {weather_data}")


# ============================================================================
# EXAMPLE 2: Batch Collection for Multiple Cities
# ============================================================================

def example_batch_collection():
    """
    Collect weather for multiple cities and save all at once.
    Best for: Saving multiple records efficiently.
    """
    from data_storage import initialize_storage, save_weather_batch
    from weather_service import fetch_weather_data
    
    initialize_storage()
    
    cities = ['London', 'Paris', 'Tokyo', 'New York', 'Sydney']
    weather_records = []
    
    # Fetch data for all cities
    for city in cities:
        success, weather = fetch_weather_data(city, 'metric')
        if success:
            weather_records.append(weather)
        else:
            print(f"Failed to fetch weather for {city}")
    
    # Save all records at once
    if weather_records:
        save_success, message = save_weather_batch(weather_records)
        print(message)


# ============================================================================
# EXAMPLE 3: Retrieve and Display Historical Data
# ============================================================================

def example_retrieve_and_display():
    """
    Get historical weather data and display it.
    Best for: Analyzing stored weather data.
    """
    from data_storage import get_weather_data
    
    # Get last 50 records for London
    london_records = get_weather_data(city='London', limit=50)
    
    print(f"Found {len(london_records)} records for London:\n")
    
    for record in london_records:
        dt = record['datetime']
        city = record['city']
        temp = record['temperature']
        humidity = record['humidity']
        condition = record['condition']
        
        print(f"{dt} | {city}: {temp}°C, {humidity}%, {condition}")


# ============================================================================
# EXAMPLE 4: Flask API Endpoint for Historical Data
# ============================================================================

def example_flask_endpoint():
    """
    Add a Flask endpoint to retrieve historical data.
    Best for: Serving data to frontend/dashboard.
    
    Usage: GET /api/weather/history?city=London&limit=100
    """
    from flask import Flask, request, jsonify
    from data_storage import get_weather_data, initialize_storage
    from helpers import error_response, success_response
    
    app = Flask(__name__)
    
    # Initialize storage at startup
    @app.before_first_request
    def startup():
        initialize_storage()
    
    @app.route('/api/weather/history', methods=['GET'])
    def weather_history():
        """
        Get historical weather data
        
        Query parameters:
            - city (optional): Filter by city name
            - limit (optional): Max records (default 100)
        """
        try:
            city = request.args.get('city', None)
            limit = request.args.get('limit', 100, type=int)
            
            # Validate limit
            if limit < 1 or limit > 10000:
                return error_response(False, 'Invalid limit',
                    'Limit must be between 1 and 10000', 400)
            
            # Retrieve data
            records = get_weather_data(city=city, limit=limit)
            
            if not records:
                return error_response(False, 'No data',
                    'No weather history found', 404)
            
            # Format response
            return success_response({
                'city': city or 'All',
                'records_count': len(records),
                'data': records
            }, 200)
            
        except Exception as e:
            return error_response(False, 'Server error', str(e), 500)


# ============================================================================
# EXAMPLE 5: Scheduler Integration (Enhanced)
# ============================================================================

def example_scheduler_with_storage():
    """
    Modify the weather_scheduler to save data.
    Best for: Automated data collection.
    
    This shows how to integrate with the existing scheduler.
    """
    import schedule
    import time
    from datetime import datetime
    from data_storage import initialize_storage, save_weather_batch
    from weather_service import fetch_weather_data
    from helpers import setup_logger
    
    logger = setup_logger(__name__)
    
    # Initialize storage once
    initialize_storage()
    
    CITIES = ['London', 'Paris', 'Tokyo', 'New York', 'Sydney']
    COLLECTION_INTERVAL = 5  # minutes
    
    def collect_weather():
        """Collect weather for all cities and save to storage"""
        logger.info(f"Collecting weather at {datetime.now()}")
        
        weather_records = []
        
        for city in CITIES:
            success, weather = fetch_weather_data(city, 'metric')
            if success:
                weather_records.append(weather)
            else:
                logger.error(f"Failed to fetch {city}: {weather}")
        
        # Save all records
        if weather_records:
            save_success, message = save_weather_batch(weather_records)
            logger.info(message)
        else:
            logger.warning("No weather data collected")
    
    # Schedule the collection
    schedule.every(COLLECTION_INTERVAL).minutes.do(collect_weather)
    
    # Run scheduler
    logger.info(f"Started weather collection every {COLLECTION_INTERVAL} minutes")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Weather collection stopped")


# ============================================================================
# EXAMPLE 6: Check Storage Statistics
# ============================================================================

def example_storage_stats():
    """
    Get and display storage statistics.
    Best for: Monitoring data growth.
    """
    from data_storage import get_storage_stats
    
    stats = get_storage_stats()
    
    print("Storage Statistics:")
    print(f"  Type: {stats['storage_type']}")
    print(f"  Directory: {stats['storage_dir']}")
    print(f"  Total Records: {stats['record_count']}")
    print(f"  File Size: {stats['file_size_mb']} MB")


# ============================================================================
# EXAMPLE 7: Export SQLite to CSV
# ============================================================================

def example_export_sqlite_to_csv():
    """
    Export all SQLite data to CSV format.
    Best for: Sharing data or switching storage types.
    """
    from data_storage import export_to_csv_from_sqlite, STORAGE_TYPE
    
    if STORAGE_TYPE != 'sqlite':
        print("This example only works with SQLite storage")
        return
    
    success, message = export_to_csv_from_sqlite('weather_export.csv')
    print(message)
    
    if success:
        print("Data exported! You can now open it in Excel.")


# ============================================================================
# EXAMPLE 8: Complete App with Storage
# ============================================================================

def example_complete_app():
    """
    Complete Flask app demonstrating storage integration.
    Best for: Understanding full workflow.
    """
    from flask import Flask, request, jsonify
    from data_storage import initialize_storage, save_weather_data, get_weather_data
    from weather_service import fetch_weather_data, validate_city
    from helpers import setup_logger, error_response, success_response
    
    app = Flask(__name__)
    logger = setup_logger(__name__)
    
    @app.before_first_request
    def startup():
        """Initialize storage when app starts"""
        success, message = initialize_storage()
        logger.info(message)
    
    @app.route('/weather', methods=['GET'])
    def get_weather_endpoint():
        """Fetch fresh weather and save it"""
        try:
            city = request.args.get('city', '').strip()
            
            if not city:
                return error_response(False, 'Missing city', 
                    'City parameter is required', 400)
            
            # Validate city
            is_valid, error = validate_city(city)
            if not is_valid:
                return error_response(False, 'Invalid city', error, 400)
            
            # Fetch weather
            success, weather = fetch_weather_data(city, 'metric')
            
            if not success:
                return error_response(False, 'API error', weather, 500)
            
            # Save to storage
            save_success, save_msg = save_weather_data(weather)
            logger.info(save_msg)
            
            return success_response(weather, 200)
            
        except Exception as e:
            logger.exception(f"Error in get_weather: {str(e)}")
            return error_response(False, 'Error', str(e), 500)
    
    @app.route('/weather/history', methods=['GET'])
    def get_history():
        """Retrieve historical weather data"""
        try:
            city = request.args.get('city', None)
            limit = request.args.get('limit', 100, type=int)
            
            records = get_weather_data(city=city, limit=limit)
            
            if not records:
                return error_response(False, 'No data', 
                    'No weather history found', 404)
            
            return success_response({
                'city': city or 'All',
                'records': records
            }, 200)
            
        except Exception as e:
            logger.exception(f"Error in get_history: {str(e)}")
            return error_response(False, 'Error', str(e), 500)
    
    return app


# ============================================================================
# EXAMPLE 9: Data Cleanup (Optional)
# ============================================================================

def example_cleanup_old_data():
    """
    Delete records older than a certain date (SQLite only).
    Best for: Maintenance and storage management.
    """
    import sqlite3
    from data_storage import STORAGE_TYPE, STORAGE_DIR, SQLITE_DB
    from helpers import setup_logger
    import os
    
    logger = setup_logger(__name__)
    
    if STORAGE_TYPE != 'sqlite':
        logger.error("Cleanup only works with SQLite storage")
        return
    
    try:
        db_path = os.path.join(STORAGE_DIR, SQLITE_DB)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete records older than 30 days
        cursor.execute('''
            DELETE FROM weather_data
            WHERE datetime < datetime('now', '-30 days')
        ''')
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted {deleted_count} old records")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")


# ============================================================================
# Running Examples
# ============================================================================

if __name__ == '__main__':
    print("Weather Data Storage Integration Examples\n")
    print("=" * 50)
    
    # Uncomment to run individual examples:
    
    # print("\nExample 1: Collect and Store Single Record")
    # example_collect_and_store()
    
    # print("\nExample 2: Batch Collection")
    # example_batch_collection()
    
    # print("\nExample 3: Retrieve and Display")
    # example_retrieve_and_display()
    
    # print("\nExample 6: Storage Statistics")
    # example_storage_stats()
    
    print("\nTo run individual examples, uncomment them in the main block")
    print("\nFor Flask apps (Example 4, 8), use:")
    print("  from example_storage_integration import example_complete_app")
    print("  app = example_complete_app()")
    print("  app.run()")
