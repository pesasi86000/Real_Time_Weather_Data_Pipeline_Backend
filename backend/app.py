from flask import Flask, jsonify, request
from helpers import setup_logger, error_response, success_response
from weather_service import fetch_weather_data, validate_city
from config import OPENWEATHER_API_KEY, FLASK_HOST, FLASK_PORT, FLASK_DEBUG, MAX_BATCH_CITIES, VALID_UNITS, DEFAULT_UNITS

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logger = setup_logger(__name__)


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
        
        # Fetch weather using the service
        success, result = fetch_weather_data(city, units)
        
        if not success:
            logger.warning(f"Failed to fetch weather for {city}: {result}")
            
            # Determine appropriate HTTP status code based on error message
            if 'not found' in result.lower():
                return error_response(False, 'City not found', result, 404)
            elif 'invalid' in result.lower() and 'api' in result.lower():
                return error_response(False, 'Authentication error', result, 401)
            elif 'rate limit' in result.lower() or 'too many' in result.lower():
                return error_response(False, 'Rate limit exceeded', result, 429)
            elif 'timeout' in result.lower():
                return error_response(False, 'Service unavailable', result, 503)
            else:
                return error_response(False, 'Internal server error', result, 500)
        
        # Success - return weather data with success flag
        logger.info(f"Successfully fetched weather for {city}")
        return success_response(result, 200)
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_weather: {str(e)}")
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
            
            # Fetch weather data
            success, result = fetch_weather_data(city, units)
            
            if success:
                results['successful'].append(result)
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
        
        # Return response
        if results['successful']:
            logger.info(f"Successfully fetched weather for {results['successful_count']}/{len(cities)} cities")
            return jsonify(results), 200
        else:
            logger.error("Failed to fetch weather for any city")
            return jsonify(results), 400
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_weather_batch: {str(e)}")
        return error_response(False, 'Internal server error',
                            'An unexpected error occurred. Please try again later.', 500)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Check if API key is configured
    api_key_status = 'configured' if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'your_api_key_here' else 'not configured'
    
    return jsonify({
        'status': 'Backend is running',
        'api_key_status': api_key_status,
        'version': '1.0'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response(False, 'Not found',
                        'The requested endpoint does not exist', 404)


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors (method not allowed)"""
    return error_response(False, 'Method not allowed',
                        'The HTTP method used is not allowed for this endpoint', 405)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.exception("Internal server error")
    return error_response(False, 'Internal server error',
                        'An unexpected error occurred. Please try again later.', 500)


if __name__ == '__main__':
    # Check API key on startup
    if not OPENWEATHER_API_KEY:
        logger.warning("⚠️  OPENWEATHER_API_KEY not set in environment. API requests will fail.")
    elif OPENWEATHER_API_KEY == 'your_api_key_here':
        logger.warning("⚠️  OPENWEATHER_API_KEY is set to placeholder value. Update .env file with real key.")
    else:
        logger.info("✓ OPENWEATHER_API_KEY is configured")
    
    # Run Flask app
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
