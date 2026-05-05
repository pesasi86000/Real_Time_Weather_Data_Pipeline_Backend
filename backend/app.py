from flask import Flask, jsonify, request
from dotenv import load_dotenv
import logging
import os

# Import service modules
from weather_service import fetch_weather_data

# Load environment variables
load_dotenv()

# Get API key status for health check
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch real-time weather data from OpenWeather API
    
    Query parameters:
        - city (required): City name (e.g., 'London' or 'London,GB')
        - units (optional): 'metric' (Celsius) or 'imperial' (Fahrenheit), default 'metric'
    
    Example: /weather?city=London&units=metric
    """
    try:
        # Get and validate input parameters
        city = request.args.get('city', '').strip()
        units = request.args.get('units', 'metric').lower()
        
        if not city:
            logger.warning("Weather request missing city parameter")
            return jsonify({
                'error': 'Missing required parameter',
                'message': 'city parameter is required',
                'example': '/weather?city=London'
            }), 400
        
        if units not in ['metric', 'imperial']:
            logger.warning(f"Invalid units parameter: {units}")
            return jsonify({
                'error': 'Invalid parameter',
                'message': "units must be 'metric' or 'imperial'",
                'example': '/weather?city=London&units=metric'
            }), 400
        
        # Fetch weather using the service
        success, result = fetch_weather_data(city, units)
        
        if not success:
            # Result is an error message
            logger.warning(f"Failed to fetch weather for {city}: {result}")
            
            # Return appropriate error code based on message
            if 'not found' in result.lower():
                status_code = 404
            elif 'api key' in result.lower():
                status_code = 401
            elif 'rate limit' in result.lower():
                status_code = 429
            else:
                status_code = 500
            
            return jsonify({
                'error': 'Failed to fetch weather',
                'message': result
            }), status_code
        
        # Success - return weather data
        logger.info(f"Successfully fetched weather for {city}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_weather: {str(e)}")
        return jsonify({
            'error': 'Unexpected error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500


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
                return jsonify({
                    'error': 'Missing required parameter',
                    'message': 'cities parameter is required',
                    'example': '/weather/batch?cities=London,Paris,Tokyo'
                }), 400
            
            cities = [city.strip() for city in cities_param.split(',') if city.strip()]
        
        # Handle POST request
        elif request.method == 'POST':
            data = request.get_json()
            
            if not data or 'cities' not in data:
                logger.warning("Batch weather request missing cities in body")
                return jsonify({
                    'error': 'Missing required field',
                    'message': 'cities field is required in JSON body',
                    'example': '{"cities": ["London", "Paris", "Tokyo"], "units": "metric"}'
                }), 400
            
            cities = data.get('cities', [])
            units = data.get('units', 'metric').lower()
            
            if not isinstance(cities, list):
                return jsonify({
                    'error': 'Invalid format',
                    'message': 'cities must be a list'
                }), 400
        
        # Validate cities list
        if not cities:
            return jsonify({
                'error': 'Empty cities list',
                'message': 'At least one city is required'
            }), 400
        
        if units not in ['metric', 'imperial']:
            logger.warning(f"Invalid units parameter: {units}")
            return jsonify({
                'error': 'Invalid parameter',
                'message': "units must be 'metric' or 'imperial'",
                'example': '/weather/batch?cities=London,Paris&units=metric'
            }), 400
        
        # Fetch weather for all cities
        results = {
            'successful': [],
            'failed': [],
            'total_requested': len(cities)
        }
        
        for city in cities:
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
        
        # Return appropriate response
        if results['successful']:
            results['successful_count'] = len(results['successful'])
            results['failed_count'] = len(results['failed'])
            logger.info(f"Successfully fetched weather for {len(results['successful'])}/{len(cities)} cities")
            return jsonify(results), 200
        else:
            logger.error("Failed to fetch weather for any city")
            return jsonify(results), 400
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_weather_batch: {str(e)}")
        return jsonify({
            'error': 'Unexpected error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500


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
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/weather', '/health']
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors (method not allowed)"""
    return jsonify({
        'error': 'Method not allowed',
        'message': f'The HTTP method used is not allowed for this endpoint'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.exception("Internal server error")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred on the server'
    }), 500


if __name__ == '__main__':
    # Check API key on startup
    if not OPENWEATHER_API_KEY:
        logger.warning("⚠️  OPENWEATHER_API_KEY not set in environment. API requests will fail.")
    elif OPENWEATHER_API_KEY == 'your_api_key_here':
        logger.warning("⚠️  OPENWEATHER_API_KEY is set to placeholder value. Update .env file with real key.")
    else:
        logger.info("✓ OPENWEATHER_API_KEY is configured")
    
    # Run Flask app in debug mode (change to False in production)
    app.run(debug=True, host='0.0.0.0', port=5000)
