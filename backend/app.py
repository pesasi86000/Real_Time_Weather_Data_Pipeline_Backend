from flask import Flask, jsonify, request, render_template, send_file
import time
from helpers import setup_logger, error_response, success_response, map_error_to_status
from weather_service import fetch_weather_data, validate_city
from response_formatter import format_weather_for_dashboard, format_weather_for_api, create_error_response
from config import OPENWEATHER_API_KEY, FLASK_HOST, FLASK_PORT, FLASK_DEBUG, MAX_BATCH_CITIES, VALID_UNITS, DEFAULT_UNITS
from data_storage import get_weather_data, get_storage_stats, initialize_storage
from data_cache import weather_cache, batch_cache
from performance_monitor import performance_monitor
from alert_manager import alert_manager
from resilience import rate_limiter, api_circuit_breaker

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Setup logging
logger = setup_logger(__name__)

# Request timing middleware
@app.before_request
def before_request():
    """Record request start time"""
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Record performance metrics after request"""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        endpoint = request.endpoint or 'unknown'
        success = 200 <= response.status_code < 300
        performance_monitor.record_request(endpoint, duration, success)
    return response


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch real-time weather data from OpenWeather API
    
    Query parameters:
        - city (required): City name (e.g., 'London' or 'London,GB')
        - units (optional): 'metric' (Celsius) or 'imperial' (Fahrenheit), default 'metric'
    
    Returns:
        200: Weather data for the city
        400: Invalid city format or missing required parameter
        404: City not found
        401: Invalid API key
        429: Rate limit exceeded
        500: Server error
    
    Example: /weather?city=London&units=metric
    """
    try:
        # Get and validate input parameters
        city = request.args.get('city', '').strip()
        units = request.args.get('units', 'metric').lower()
        
        # Validate city parameter
        if not city:
            logger.warning("Weather request missing city parameter")
            return error_response(False, 'Missing required parameter', 
                                'The "city" parameter is required', 400)
        
        # Validate city format
        is_valid, validation_error = validate_city(city)
        if not is_valid:
            logger.warning(f"Invalid city format: {city} - {validation_error}")
            return error_response(False, 'Invalid city format', validation_error, 400)
        
        # Validate units parameter
        if units not in VALID_UNITS:
            logger.warning(f"Invalid units parameter: {units}")
            return error_response(False, 'Invalid parameter',
                                f"The 'units' parameter must be one of: {', '.join(VALID_UNITS)}", 400)
        
        # Check cache first
        cache_key = f"weather:{city.lower()}:{units}"
        cached = weather_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {city} ({units})")
            return success_response(cached, 200)

        # Fetch weather using the service
        success, result = fetch_weather_data(city, units)
        
        if not success:
            logger.warning(f"Failed to fetch weather for {city}: {result}")
            error_title, status_code = map_error_to_status(result)
            return error_response(False, error_title, result, status_code)
        
        # Process alerts
        alert_manager.process_weather(city, result)

        # Success - format, cache and return weather data
        logger.info(f"Successfully fetched weather for {city}")
        formatted_data = format_weather_for_api(result)
        weather_cache.set(cache_key, formatted_data)
        return success_response(formatted_data, 200)
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_weather: {str(e)}")
        return error_response(False, 'Internal server error',
                            'An unexpected error occurred. Please try again later.', 500)


@app.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    Fetch weather data optimized for dashboard UI
    
    Query parameters:
        - city (required): City name (e.g., 'London' or 'London,GB')
        - units (optional): 'metric' (Celsius) or 'imperial' (Fahrenheit), default 'metric'
    
    Returns:
        200: Dashboard-formatted weather data with all fields needed for UI
        400: Invalid parameters
        404: City not found
        500: Server error
        
    Response includes:
        - location: City and country information
        - current_weather: All weather metrics with proper organization
        - alerts: Active alerts with severity levels
        - units: Symbol reference for the UI
        - timestamp: Data fetch timestamp
    
    Example: /dashboard?city=London&units=metric
    """
    try:
        # Get and validate input parameters
        city = request.args.get('city', '').strip()
        units = request.args.get('units', 'metric').lower()
        
        # Validate city parameter
        if not city:
            logger.warning("Dashboard request missing city parameter")
            return error_response(False, 'Missing required parameter',
                                'The "city" parameter is required', 400)
        
        # Validate city format
        is_valid, validation_error = validate_city(city)
        if not is_valid:
            logger.warning(f"Invalid city format: {city} - {validation_error}")
            return error_response(False, 'Invalid city format', validation_error, 400)
        
        # Validate units parameter
        if units not in VALID_UNITS:
            logger.warning(f"Invalid units parameter: {units}")
            return error_response(False, 'Invalid parameter',
                                f"The 'units' parameter must be one of: {', '.join(VALID_UNITS)}", 400)
        
        # Check cache first
        cache_key = f"dashboard:{city.lower()}:{units}"
        cached = weather_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for dashboard {city} ({units})")
            return success_response(cached, 200)

        # Fetch weather using the service
        success, result = fetch_weather_data(city, units)
        
        if not success:
            logger.warning(f"Failed to fetch weather for {city}: {result}")
            error_title, status_code = map_error_to_status(result)
            return error_response(False, error_title, result, status_code)
        
        # Process and track alerts
        alert_manager.process_weather(city, result)

        # Format data specifically for dashboard, cache and return
        logger.info(f"Successfully fetched dashboard data for {city}")
        dashboard_data = format_weather_for_dashboard(result)
        weather_cache.set(cache_key, dashboard_data)
        return success_response(dashboard_data, 200)
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_dashboard_data: {str(e)}")
        return error_response(False, 'Internal server error',
                            'An unexpected error occurred. Please try again later.', 500)


@app.route('/weather/batch', methods=['GET', 'POST'])
def get_weather_batch():
    """
    Fetch real-time weather data for multiple cities
    
    GET Query parameters:
        - cities (required): Comma-separated city names (e.g., 'London,Paris,Tokyo')
        - units (optional): 'metric' (Celsius) or 'imperial' (Fahrenheit), default 'metric'
    
    POST JSON body:
        {
            "cities": ["London", "Paris", "Tokyo"],
            "units": "metric"
        }
    
    Returns:
        200: Batch results with successful and failed cities
        400: Invalid request format or missing required parameters
    
    Example GET: /weather/batch?cities=London,Paris,Tokyo&units=metric
    Example POST: {"cities": ["London", "Paris", "Tokyo"], "units": "metric"}
    """
    try:
        cities = []
        units = 'metric'
        
        # Handle GET request
        if request.method == 'GET':
            cities_param = request.args.get('cities', '').strip()
            units = request.args.get('units', 'metric').lower()
            
            if not cities_param:
                logger.warning("Batch weather request missing cities parameter")
                return error_response(False, 'Missing required parameter',
                                    'The "cities" parameter is required (comma-separated)', 400)
            
            cities = [city.strip() for city in cities_param.split(',') if city.strip()]
        
        # Handle POST request
        elif request.method == 'POST':
            data = request.get_json()
            
            if not data or 'cities' not in data:
                logger.warning("Batch weather request missing cities in body")
                return error_response(False, 'Missing required field',
                                    'The "cities" field is required in JSON body', 400)
            
            cities = data.get('cities', [])
            units = data.get('units', 'metric').lower()
            
            if not isinstance(cities, list):
                return error_response(False, 'Invalid format',
                                    'The "cities" field must be a list of city names', 400)
        
        # Validate cities list
        if not cities:
            return error_response(False, 'Empty cities list',
                                'At least one city is required', 400)
        
        # Limit batch size for performance
        if len(cities) > MAX_BATCH_CITIES:
            return error_response(False, 'Too many cities',
                                f'Maximum {MAX_BATCH_CITIES} cities per request', 400)
        
        # Validate units parameter
        if units not in VALID_UNITS:
            logger.warning(f"Invalid units parameter: {units}")
            return error_response(False, 'Invalid parameter',
                                f"The 'units' parameter must be one of: {', '.join(VALID_UNITS)}", 400)
        
        # Check batch cache before fetching
        sorted_cities = sorted(c.strip().lower() for c in cities if c.strip())
        batch_key = f"batch:{','.join(sorted_cities)}:{units}"
        cached_batch = batch_cache.get(batch_key)
        if cached_batch:
            logger.info(f"Batch cache hit for {len(sorted_cities)} cities ({units})")
            return jsonify(cached_batch), 200

        # Validate and fetch weather for all cities
        results = {
            'success': True,
            'total_requested': len(cities),
            'successful': [],
            'failed': [],
            'invalid_format': []
        }
        
        for city in cities:
            # Validate city format first
            is_valid, validation_error = validate_city(city)
            if not is_valid:
                results['invalid_format'].append({
                    'city': city,
                    'error': validation_error
                })
                logger.warning(f"Invalid city format: {city} - {validation_error}")
                continue
            
            # Serve from per-city cache when available
            city_cache_key = f"weather:{city.strip().lower()}:{units}"
            cached_city = weather_cache.get(city_cache_key)
            if cached_city:
                results['successful'].append(cached_city)
                logger.info(f"✓ Cache hit for {city}")
                continue

            # Fetch weather data
            success, result = fetch_weather_data(city, units)
            
            if success:
                formatted = format_weather_for_api(result)
                weather_cache.set(city_cache_key, formatted)
                results['successful'].append(formatted)
                logger.info(f"✓ Fetched weather for {city}")
            else:
                results['failed'].append({
                    'city': city,
                    'error': result
                })
                logger.warning(f"✗ Failed to fetch weather for {city}: {result}")
        
        # Update counts
        results['successful_count'] = len(results['successful'])
        results['failed_count'] = len(results['failed'])
        results['invalid_format_count'] = len(results['invalid_format'])
        
        # Cache successful batch responses
        if results['successful']:
            batch_cache.set(batch_key, results)
            logger.info(f"Successfully fetched weather for {results['successful_count']}/{len(cities)} cities")
            return jsonify(results), 200
        else:
            logger.error("Failed to fetch weather for any city")
            return jsonify(results), 400
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_weather_batch: {str(e)}")
        return error_response(False, 'Internal server error',
                            'An unexpected error occurred. Please try again later.', 500)


@app.route('/weather/history', methods=['GET'])
def get_weather_history():
    """
    Retrieve historical weather data for frontend consumption.

    Query parameters:
        - city (optional): Filter by city name (e.g., 'London'). Returns all cities if omitted.
        - limit (optional): Maximum number of records to return (1-500, default 100).

    Returns:
        200: Historical weather records sorted newest-first
        400: Invalid query parameters
        500: Storage error

    Example: /weather/history?city=London&limit=50
    """
    try:
        city = request.args.get('city', '').strip() or None
        limit_param = request.args.get('limit', '100').strip()

        # Validate limit
        try:
            limit = int(limit_param)
            if limit < 1 or limit > 500:
                raise ValueError
        except ValueError:
            return error_response(False, 'Invalid parameter',
                                  'The "limit" parameter must be an integer between 1 and 500', 400)

        # Validate city format if provided
        if city:
            is_valid, validation_error = validate_city(city)
            if not is_valid:
                logger.warning(f"Invalid city format in history request: {city} - {validation_error}")
                return error_response(False, 'Invalid city format', validation_error, 400)

        records = get_weather_data(city=city, limit=limit)
        stats = get_storage_stats()

        logger.info(f"Returned {len(records)} historical records (city={city}, limit={limit})")
        return success_response({
            'records': records,
            'count': len(records),
            'filters': {
                'city': city,
                'limit': limit
            },
            'storage': {
                'type': stats.get('storage_type'),
                'total_records': stats.get('record_count')
            }
        }, 200)

    except Exception as e:
        logger.exception(f"Unexpected error in get_weather_history: {str(e)}")
        return error_response(False, 'Internal server error',
                              'An unexpected error occurred. Please try again later.', 500)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    api_key_status = 'configured' if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'your_api_key_here' else 'not configured'
    storage_stats = get_storage_stats()

    return jsonify({
        'status': 'Backend is running',
        'api_key_status': api_key_status,
        'storage': {
            'type': storage_stats.get('storage_type'),
            'record_count': storage_stats.get('record_count'),
            'file_size_mb': storage_stats.get('file_size_mb')
        },
        'version': '1.0'
    }), 200


@app.route('/', methods=['GET'])
@app.route('/dashboard-ui', methods=['GET'])
def dashboard_ui():
    """
    Serve the weather dashboard UI
    
    Returns:
        HTML: Interactive weather dashboard page
    """
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.exception(f"Error loading dashboard: {str(e)}")
        return error_response(False, 'Dashboard error',
                            'Failed to load dashboard interface', 500)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response(False, 'Not found',
                        'The requested endpoint does not exist', 404)


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return error_response(False, 'Method not allowed',
                        'The HTTP method is not allowed for this endpoint', 405)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.exception("Internal server error")
    return error_response(False, 'Internal server error',
                        'An unexpected error occurred. Please try again later.', 500)


@app.route('/weather/alerts', methods=['GET'])
def get_weather_alerts():
    """
    Get active weather alerts for a city or all monitored cities.

    Query parameters:
        - city (optional): City name to get alerts for. Returns all active alerts if omitted.

    Returns:
        200: Active alerts data
        400: Invalid city format
        500: Server error

    Example: /weather/alerts?city=London
    """
    try:
        city = request.args.get('city', '').strip() or None

        if city:
            is_valid, validation_error = validate_city(city)
            if not is_valid:
                return error_response(False, 'Invalid city format', validation_error, 400)

            # Fetch fresh weather data and evaluate alerts
            units = request.args.get('units', 'metric').lower()
            success, result = fetch_weather_data(city, units)

            if not success:
                error_title, status_code = map_error_to_status(result)
                return error_response(False, error_title, result, status_code)

            alerts_result = alert_manager.process_weather(city, result)
            logger.info(f"Alerts evaluated for {city}: {len(alerts_result.get('alerts', []))} alert(s)")
            return success_response({
                'city': city,
                'alerts_active': alerts_result['alerts_active'],
                'alerts': alerts_result.get('alerts', []),
                'alert_count': len(alerts_result.get('alerts', []))
            }, 200)

        # Return all active alerts across all tracked cities
        summary = alert_manager.get_alert_summary()
        active_alerts = alert_manager.get_active_alerts()
        logger.info(f"Returning global alert summary: {summary['total_cities_with_alerts']} cities affected")
        return success_response({
            'summary': summary,
            'active_alerts': active_alerts
        }, 200)

    except Exception as e:
        logger.exception(f"Unexpected error in get_weather_alerts: {str(e)}")
        return error_response(False, 'Internal server error',
                            'An unexpected error occurred. Please try again later.', 500)


@app.route('/system/health', methods=['GET'])
def system_health():
    """
    Detailed system health and performance metrics.

    Returns:
        200: System health status, API performance stats, cache stats, resilience metrics, and alert summary
    """
    try:
        storage_stats = get_storage_stats()
        perf_stats = performance_monitor.get_stats()
        health_status = performance_monitor.get_health_status()
        cache_stats = weather_cache.get_stats()
        alert_summary = alert_manager.get_alert_summary()
        api_key_ok = bool(OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'your_api_key_here')
        
        # Get resilience metrics
        circuit_breaker_state = api_circuit_breaker.get_state()
        rate_limiter_stats = {
            'max_requests_per_window': rate_limiter.max_requests,
            'time_window_seconds': rate_limiter.time_window,
            'requests_made': rate_limiter.get_request_count()
        }

        return success_response({
            'status': health_status,
            'api_key_configured': api_key_ok,
            'storage': {
                'type': storage_stats.get('storage_type'),
                'total_records': storage_stats.get('record_count'),
                'file_size_mb': storage_stats.get('file_size_mb')
            },
            'performance': {
                'avg_response_time_s': round(perf_stats.get('avg_response_time', 0), 3),
                'min_response_time_s': round(perf_stats.get('min_response_time', 0), 3),
                'max_response_time_s': round(perf_stats.get('max_response_time', 0), 3),
                'total_requests': perf_stats.get('total_requests', 0),
                'endpoint_stats': perf_stats.get('endpoint_stats', {})
            },
            'cache': cache_stats,
            'resilience': {
                'circuit_breaker': {
                    'state': circuit_breaker_state['state'],
                    'failure_count': circuit_breaker_state['failure_count'],
                    'success_count': circuit_breaker_state['success_count']
                },
                'rate_limiter': rate_limiter_stats
            },
            'alerts': alert_summary,
            'version': '2.0'
        }, 200)

    except Exception as e:
        logger.exception(f"Error in system_health: {str(e)}")
        return error_response(False, 'Internal server error',
                            'Failed to retrieve system health metrics', 500)


@app.route('/system/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear the weather data cache.
    Returns:
        200: Cache cleared successfully
    """
    try:
        weather_cache.clear()
        batch_cache.clear()
        logger.info("Weather data cache cleared via API")
        return success_response({'message': 'Cache cleared successfully'}, 200)
    except Exception as e:
        logger.exception(f"Error clearing cache: {str(e)}")
        return error_response(False, 'Internal server error', 'Failed to clear cache', 500)


if __name__ == '__main__':
    logger.info("Initializing storage...")
    initialize_storage()
    logger.info(f"Starting Real-Time Weather Data Pipeline Backend on {FLASK_HOST}:{FLASK_PORT}")
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.exception("Internal server error")
    return error_response(False, 'Internal server error',
                        'An unexpected error occurred. Please try again later.', 500)


if __name__ == '__main__':
    # Initialize data storage on startup
    storage_ok, storage_msg = initialize_storage()
    if storage_ok:
        logger.info(f"✓ Storage initialized: {storage_msg}")
    else:
        logger.warning(f"⚠️  Storage initialization failed: {storage_msg}")

    # Check API key on startup
    if not OPENWEATHER_API_KEY:
        logger.warning("⚠️  OPENWEATHER_API_KEY not set in environment. API requests will fail.")
    elif OPENWEATHER_API_KEY == 'your_api_key_here':
        logger.warning("⚠️  OPENWEATHER_API_KEY is set to placeholder value. Update .env file with real key.")
    else:
        logger.info("✓ OPENWEATHER_API_KEY is configured")
    
    # Run Flask app
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
