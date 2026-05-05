from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Required fields in weather response
REQUIRED_FIELDS = {
    'name': 'city',
    'main': ['temp', 'humidity'],
    'weather': ['main', 'description'],
    'wind': ['speed']
}


def validate_api_key():
    """Validate that API key is configured and valid"""
    if not OPENWEATHER_API_KEY:
        logger.error("OpenWeather API key not configured")
        return False, jsonify({
            'error': 'API key not configured',
            'message': 'Set OPENWEATHER_API_KEY environment variable'
        }), 500
    
    if OPENWEATHER_API_KEY == 'your_api_key_here' or len(OPENWEATHER_API_KEY) < 10:
        logger.error("Invalid API key format")
        return False, jsonify({
            'error': 'Invalid API key',
            'message': 'API key is not properly configured. Please set a valid key.'
        }), 500
    
    return True, None, None


def validate_required_fields(data):
    """Validate that all required fields are present in API response"""
    missing_fields = []
    
    # Check main fields
    if 'name' not in data:
        missing_fields.append('city name')
    
    if 'main' not in data:
        missing_fields.append('temperature and humidity')
    else:
        if 'temp' not in data['main']:
            missing_fields.append('temperature')
        if 'humidity' not in data['main']:
            missing_fields.append('humidity')
    
    if 'weather' not in data or not data['weather']:
        missing_fields.append('weather condition')
    else:
        if 'main' not in data['weather'][0]:
            missing_fields.append('weather condition type')
    
    if 'wind' not in data or 'speed' not in data.get('wind', {}):
        missing_fields.append('wind speed')
    
    if missing_fields:
        return False, missing_fields
    
    return True, []


def parse_weather_data(data):
    """Extract and parse weather data from API response"""
    try:
        weather_info = {
            'city': data.get('name'),
            'country': data.get('sys', {}).get('country', 'Unknown'),
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'condition': data['weather'][0]['main'],
            'description': data['weather'][0].get('description', 'N/A'),
            'feels_like': data['main'].get('feels_like'),
            'pressure': data['main'].get('pressure'),
            'wind_speed': data['wind']['speed'],
            'cloudiness': data.get('clouds', {}).get('all'),
            'units': 'metric'  # Will be updated based on request
        }
        return True, weather_info
    except (KeyError, TypeError) as e:
        logger.error(f"Error parsing weather data: {str(e)}")
        return False, str(e)


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch real-time weather data from OpenWeather API
    Query parameters:
        - city (required): City name
        - units (optional): 'metric' (Celsius) or 'imperial' (Fahrenheit), default 'metric'
    """
    try:
        # Validate API key
        is_valid, error_response, status_code = validate_api_key()
        if not is_valid:
            return error_response, status_code
        
        # Get city from query parameters
        city = request.args.get('city', '').strip()
        units = request.args.get('units', 'metric').lower()
        
        # Validate input parameters
        if not city:
            logger.warning("Weather request missing city parameter")
            return jsonify({
                'error': 'Missing required parameter',
                'message': 'city parameter is required',
                'example': '/weather?city=London'
            }), 400
        
        # Validate units parameter
        if units not in ['metric', 'imperial']:
            logger.warning(f"Invalid units parameter: {units}")
            return jsonify({
                'error': 'Invalid parameter',
                'message': "units must be 'metric' or 'imperial'",
                'example': '/weather?city=London&units=metric'
            }), 400
        
        # Make API request to OpenWeather
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': units
        }
        
        try:
            response = requests.get(
                OPENWEATHER_BASE_URL,
                params=params,
                timeout=5
            )
        except requests.exceptions.Timeout:
            logger.error("OpenWeather API request timed out")
            return jsonify({
                'error': 'API request timeout',
                'message': 'OpenWeather API did not respond in time. Please try again.'
            }), 504
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to OpenWeather API")
            return jsonify({
                'error': 'Connection error',
                'message': 'Failed to connect to OpenWeather API. Check your internet connection.'
            }), 503
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            return jsonify({
                'error': 'API request failed',
                'message': str(e)
            }), 500
        
        # Handle different HTTP status codes
        if response.status_code == 401:
            logger.error("Invalid API key provided")
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid API key. Please check your OpenWeather API key.'
            }), 401
        
        elif response.status_code == 404:
            logger.warning(f"City not found: {city}")
            return jsonify({
                'error': 'City not found',
                'message': f"Could not find weather data for '{city}'. Please check the city name.",
                'suggestion': 'Try using city name in English or include country code (e.g., "London,GB")'
            }), 404
        
        elif response.status_code == 429:
            logger.warning("OpenWeather API rate limit exceeded")
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests to OpenWeather API. Please try again later.'
            }), 429
        
        elif response.status_code != 200:
            logger.error(f"OpenWeather API error: {response.status_code}")
            try:
                error_data = response.json()
                return jsonify({
                    'error': 'API error',
                    'message': error_data.get('message', f'HTTP {response.status_code}'),
                    'status_code': response.status_code
                }), response.status_code
            except:
                return jsonify({
                    'error': 'API error',
                    'message': f'OpenWeather API returned HTTP {response.status_code}',
                    'status_code': response.status_code
                }), response.status_code
        
        # Parse and validate response data
        try:
            data = response.json()
        except ValueError:
            logger.error("Invalid JSON response from OpenWeather API")
            return jsonify({
                'error': 'Invalid API response',
                'message': 'OpenWeather API returned invalid JSON'
            }), 502
        
        # Validate required fields
        is_valid, missing_fields = validate_required_fields(data)
        if not is_valid:
            logger.error(f"Missing fields in API response: {missing_fields}")
            return jsonify({
                'error': 'Incomplete API response',
                'message': 'OpenWeather API response missing required fields',
                'missing_fields': missing_fields
            }), 502
        
        # Extract weather information
        success, result = parse_weather_data(data)
        if not success:
            logger.error(f"Error parsing weather data: {result}")
            return jsonify({
                'error': 'Data parsing error',
                'message': 'Failed to parse weather data from API response'
            }), 502
        
        # Update units in response
        result['units'] = units
        
        logger.info(f"Successfully fetched weather for {city}")
        return jsonify(result), 200
    
    except Exception as e:
        logger.exception(f"Unexpected error in get_weather: {str(e)}")
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
