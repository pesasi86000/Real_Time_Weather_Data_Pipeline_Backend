"""
Weather Service Module
Handles all weather API interactions with modular, reusable functions
"""

import re
import time
import requests
from datetime import datetime
from helpers import setup_logger
from alerts_service import generate_alerts
from resilience import rate_limiter, api_circuit_breaker, retry_policy
from config import (
    OPENWEATHER_API_KEY,
    OPENWEATHER_BASE_URL,
    REQUEST_TIMEOUT,
    MIN_CITY_LENGTH,
    MAX_CITY_LENGTH,
    VALID_UNITS
)

logger = setup_logger(__name__)


# ============================================================================
# INPUT VALIDATION HELPERS
# ============================================================================

def validate_city(city):
    """
    Validate city parameter format and content
    
    Args:
        city (str): City name to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Check type and basic emptiness
    if not city or not isinstance(city, str):
        return False, "City name is required and must be a string"
    
    # Check for whitespace-only input
    if not city.strip():
        return False, "City name cannot be empty or contain only whitespace"
    
    # Check length constraints
    city_clean = city.strip()
    if len(city_clean) < MIN_CITY_LENGTH:
        return False, f"City name must be at least {MIN_CITY_LENGTH} characters long"
    
    if len(city_clean) > MAX_CITY_LENGTH:
        return False, f"City name cannot exceed {MAX_CITY_LENGTH} characters"
    
    # Check for invalid characters (allow letters, numbers, spaces, commas, hyphens, and periods)
    # This pattern allows: letters, numbers, spaces, hyphens, apostrophes, periods, and commas (for country codes)
    if not re.match(r"^[a-zA-Z0-9\s\-',.]+$", city_clean):
        return False, "City name contains invalid characters. Only letters, numbers, spaces, hyphens, apostrophes, periods, and commas are allowed"
    
    # Check for leading/trailing invalid characters
    if city_clean.startswith('-') or city_clean.startswith(',') or city_clean.startswith('.'):
        return False, "City name cannot start with a hyphen, comma, or period"
    
    if city_clean.endswith('-') or city_clean.endswith(',') or city_clean.endswith('.'):
        return False, "City name cannot end with a hyphen, comma, or period"
    
    return True, None


def validate_units(units):
    """
    Validate units parameter
    
    Args:
        units (str): Units parameter to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if units not in VALID_UNITS:
        return False, f"Units must be one of: {', '.join(VALID_UNITS)}"
    
    return True, None


def validate_api_key():
    """
    Validate that API key is configured
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == 'your_api_key_here':
        return False, "OpenWeather API key not configured"
    
    return True, None


# ============================================================================
# API REQUEST HELPERS
# ============================================================================

def build_request_params(city, units):
    """
    Build parameters for OpenWeather API request
    
    Args:
        city (str): City name
        units (str): Temperature units
        
    Returns:
        dict: Request parameters
    """
    return {
        'q': city.strip(),
        'appid': OPENWEATHER_API_KEY,
        'units': units
    }


def make_weather_request(params):
    """
    Make HTTP request to OpenWeather API with rate limiting and resilience
    
    Args:
        params (dict): Request parameters
        
    Returns:
        tuple: (success: bool, response: Response or error_message: str)
    """
    # Check rate limit
    if not rate_limiter.is_allowed():
        retry_after = rate_limiter.get_retry_after()
        error_msg = f"Rate limited. Please retry after {retry_after:.1f}s"
        logger.warning(error_msg)
        return False, error_msg
    
    # Check circuit breaker
    if not api_circuit_breaker.can_attempt():
        state = api_circuit_breaker.get_state()
        error_msg = f"API temporarily unavailable (Circuit breaker: {state['state']})"
        logger.warning(error_msg)
        return False, error_msg
    
    # Retry logic with exponential backoff
    city = params.get('q', 'Unknown')
    for attempt in range(retry_policy.max_attempts):
        try:
            response = requests.get(
                OPENWEATHER_BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            
            # Record success in circuit breaker
            api_circuit_breaker.record_success()
            return True, response
            
        except requests.exceptions.Timeout:
            error_msg = "Request timeout. API server not responding."
            logger.error(f"Attempt {attempt + 1}: {error_msg} for {city}")
            
            if not retry_policy.should_retry(attempt, 'timeout'):
                api_circuit_breaker.record_failure()
                return False, error_msg
            
            if attempt < retry_policy.max_attempts - 1:
                delay = retry_policy.get_retry_delay(attempt)
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error. Unable to reach weather API."
            logger.error(f"Attempt {attempt + 1}: {error_msg} for {city}")
            
            if not retry_policy.should_retry(attempt, 'connection'):
                api_circuit_breaker.record_failure()
                return False, error_msg
            
            if attempt < retry_policy.max_attempts - 1:
                delay = retry_policy.get_retry_delay(attempt)
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(f"Attempt {attempt + 1}: {error_msg} for {city}")
            
            if not retry_policy.should_retry(attempt, 'request'):
                api_circuit_breaker.record_failure()
                return False, error_msg
            
            if attempt < retry_policy.max_attempts - 1:
                delay = retry_policy.get_retry_delay(attempt)
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
    
    # All retries exhausted
    api_circuit_breaker.record_failure()
    logger.error(f"Max retry attempts reached for {city}")
    return False, "Failed to retrieve weather data after multiple attempts"


def handle_api_response(response):
    """
    Handle HTTP response from OpenWeather API with appropriate error messages
    
    Args:
        response (requests.Response): API response
        
    Returns:
        tuple: (success: bool, data: dict or error_message: str)
    """
    if response.status_code == 200:
        return True, response.json()
    
    elif response.status_code == 404:
        city = response.request.params.get('q', 'Unknown')
        logger.warning(f"City not found: {city}")
        return False, f"City '{city}' not found. Please check the spelling."
    
    elif response.status_code == 401:
        logger.error("Invalid API key")
        return False, "Invalid API key. Please check your configuration."
    
    elif response.status_code == 429:
        logger.warning("API rate limit exceeded")
        return False, "Too many requests. Please try again later."
    
    else:
        logger.error(f"API returned status {response.status_code}")
        return False, f"API error: HTTP {response.status_code}"


# ============================================================================
# DATA EXTRACTION & FORMATTING HELPERS
# ============================================================================

def extract_weather_info(api_data, units):
    """
    Extract and format weather information from API response
    Handles missing fields gracefully with validation and defaults.
    
    Args:
        api_data (dict): Raw data from OpenWeather API
        units (str): Temperature units
        
    Returns:
        dict: Formatted weather information
        
    Raises:
        ValueError: If critical fields are missing
    """
    # Validate critical fields
    required_fields = ['name', 'main', 'weather']
    for field in required_fields:
        if field not in api_data or not api_data[field]:
            logger.error(f"Missing required API field: {field}")
            raise ValueError(f"Invalid API response: missing {field}")
    
    try:
        main_data = api_data.get('main', {})
        weather_data = api_data.get('weather', [{}])[0]
        wind_data = api_data.get('wind', {})
        sys_data = api_data.get('sys', {})
        clouds_data = api_data.get('clouds', {})
        
        # Validate critical numeric values
        temperature = main_data.get('temp')
        humidity = main_data.get('humidity')
        
        if temperature is None:
            logger.error("Missing temperature in API response")
            raise ValueError("Invalid API response: temperature is required")
        
        if humidity is None:
            logger.error("Missing humidity in API response")
            raise ValueError("Invalid API response: humidity is required")
        
        # Safely convert to ensure proper types
        try:
            temperature = float(temperature)
            humidity = int(humidity)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid temperature/humidity values: {e}")
            raise ValueError(f"Invalid temperature or humidity format: {e}")
        
        # Extract data with safe defaults
        weather_info = {
            'city': api_data.get('name', 'Unknown').strip() or 'Unknown',
            'country': sys_data.get('country', 'Unknown'),
            'temperature': temperature,
            'feels_like': main_data.get('feels_like', temperature),  # Default to actual temp
            'humidity': humidity,
            'pressure': main_data.get('pressure', 0),
            'condition': weather_data.get('main', 'Unknown'),
            'description': weather_data.get('description', 'N/A'),
            'wind_speed': wind_data.get('speed', 0),
            'cloudiness': clouds_data.get('all', 0),
            'units': units,
            'fetched_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        return weather_info
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error extracting weather info: {e}")
        raise ValueError(f"Failed to process API response: {e}")


# ============================================================================
# MAIN PUBLIC FUNCTION
# ============================================================================

def fetch_weather_data(city, units='metric'):
    """
    Fetch weather data from OpenWeather API for a specific city
    
    This is the main reusable function that orchestrates the entire process:
    validates input, makes the API request, and formats the response.
    
    Args:
        city (str): City name (e.g., 'London', 'London,GB')
        units (str): 'metric' for Celsius or 'imperial' for Fahrenheit (default: 'metric')
        
    Returns:
        tuple: (success: bool, data: dict or error_message: str)
        - On success: (True, weather_dict)
        - On failure: (False, error_message)
        
    Example:
        >>> success, result = fetch_weather_data('London', 'metric')
        >>> if success:
        ...     print(f"Temperature: {result['temperature']}°C")
        ... else:
        ...     print(f"Error: {result}")
    """
    
    # Validate inputs
    is_valid, error = validate_city(city)
    if not is_valid:
        return False, error
    
    is_valid, error = validate_units(units)
    if not is_valid:
        return False, error
    
    # Check API key
    is_valid, error = validate_api_key()
    if not is_valid:
        logger.error(error)
        return False, error
    
    # Build request parameters
    params = build_request_params(city, units)
    
    # Make API request
    success, result = make_weather_request(params)
    if not success:
        return False, result
    
    # Handle API response
    success, data = handle_api_response(result)
    if not success:
        return False, data
    
    # Extract and format weather information
    try:
        weather_info = extract_weather_info(data, units)
        
        # Generate weather alerts
        weather_alerts = generate_alerts(weather_info)
        weather_info['alerts_active'] = weather_alerts['alerts_active']
        weather_info['alerts'] = weather_alerts['alerts']
        
        logger.info(f"Successfully fetched weather for {city}")
        return True, weather_info
        
    except KeyError as e:
        logger.error(f"Unexpected API response format. Missing key: {str(e)}")
        return False, "Invalid response format from API"
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
