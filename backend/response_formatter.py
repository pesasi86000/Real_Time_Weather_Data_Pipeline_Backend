"""
Response Formatter Module
Formats API responses for different client types (API vs Dashboard)
"""

from datetime import datetime
from helpers import setup_logger

logger = setup_logger(__name__)


def format_weather_for_dashboard(weather_data):
    """
    Format weather data specifically for dashboard UI consumption
    Provides a clean, well-organized JSON structure
    
    Args:
        weather_data (dict): Weather information from weather_service
        
    Returns:
        dict: Dashboard-optimized weather response
        
    Example response:
        {
            "location": {
                "city": "London",
                "country": "GB",
                "coordinates": {"latitude": 51.5085, "longitude": -0.1257}
            },
            "current_weather": {
                "temperature": 15,
                "feels_like": 14,
                "condition": "Cloudy",
                "description": "Overcast clouds",
                "humidity": 72,
                "pressure": 1013,
                "wind_speed": 3.5,
                "cloudiness": 90,
                "units": "metric"
            },
            "alerts": {
                "active": false,
                "count": 0,
                "items": []
            },
            "timestamp": "2024-04-29T15:30:45Z",
            "units": {
                "temperature": "°C",
                "wind_speed": "m/s",
                "pressure": "hPa"
            }
        }
    """
    try:
        # Determine unit symbols
        unit_symbols = get_unit_symbols(weather_data.get('units', 'metric'))
        
        # Build location info
        location = {
            'city': weather_data.get('city', 'Unknown'),
            'country': weather_data.get('country', 'Unknown'),
        }
        
        # Build current weather section
        current_weather = {
            'temperature': weather_data.get('temperature'),
            'feels_like': weather_data.get('feels_like'),
            'condition': weather_data.get('condition', 'Unknown'),
            'description': weather_data.get('description', 'No description'),
            'humidity': weather_data.get('humidity', 0),
            'pressure': weather_data.get('pressure'),
            'wind_speed': weather_data.get('wind_speed', 0),
            'cloudiness': weather_data.get('cloudiness', 0),
            'units': weather_data.get('units', 'metric')
        }
        
        # Build alerts section
        alerts_data = weather_data.get('alerts', [])
        alerts_info = {
            'active': weather_data.get('alerts_active', False),
            'count': len(alerts_data),
            'items': alerts_data
        }
        
        # Combine all sections
        response = {
            'location': location,
            'current_weather': current_weather,
            'alerts': alerts_info,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'units': unit_symbols
        }
        
        logger.info(f"Formatted weather response for {location['city']}")
        return response
        
    except Exception as e:
        logger.error(f"Error formatting weather for dashboard: {str(e)}")
        raise


def format_weather_for_api(weather_data):
    """
    Format weather data for standard API consumption
    Maintains backward compatibility while organizing structure
    
    Args:
        weather_data (dict): Weather information from weather_service
        
    Returns:
        dict: API-optimized weather response
    """
    try:
        return {
            'city': weather_data.get('city', 'Unknown'),
            'country': weather_data.get('country', 'Unknown'),
            'current_weather': {
                'temperature': weather_data.get('temperature'),
                'feels_like': weather_data.get('feels_like'),
                'humidity': weather_data.get('humidity'),
                'pressure': weather_data.get('pressure'),
                'condition': weather_data.get('condition'),
                'description': weather_data.get('description'),
                'wind_speed': weather_data.get('wind_speed'),
                'cloudiness': weather_data.get('cloudiness'),
                'units': weather_data.get('units')
            },
            'alerts': {
                'alerts_active': weather_data.get('alerts_active', False),
                'alerts': weather_data.get('alerts', [])
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
        logger.error(f"Error formatting weather for API: {str(e)}")
        raise


def format_batch_response(batch_results):
    """
    Format batch query results for dashboard
    
    Args:
        batch_results (dict): Results from batch weather fetch
            {
                'successful': [weather_data, ...],
                'failed': [{'city': 'xxx', 'error': 'yyy'}, ...]
            }
        
    Returns:
        dict: Formatted batch response
    """
    try:
        successful = [format_weather_for_dashboard(w) for w in batch_results.get('successful', [])]
        failed = batch_results.get('failed', [])
        
        return {
            'batch': {
                'total_requested': len(successful) + len(failed),
                'successful': len(successful),
                'failed': len(failed)
            },
            'weather_data': successful,
            'errors': failed,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
        logger.error(f"Error formatting batch response: {str(e)}")
        raise


def get_unit_symbols(units):
    """
    Get unit symbols for display
    
    Args:
        units (str): Units type ('metric' or 'imperial')
        
    Returns:
        dict: Unit symbols for various measurements
    """
    if units == 'metric':
        return {
            'temperature': '°C',
            'wind_speed': 'm/s',
            'pressure': 'hPa',
            'humidity': '%'
        }
    else:  # imperial
        return {
            'temperature': '°F',
            'wind_speed': 'mph',
            'pressure': 'hPa',
            'humidity': '%'
        }


def create_error_response(error_type, message, details=None):
    """
    Create a structured error response
    
    Args:
        error_type (str): Type of error (e.g., 'VALIDATION_ERROR', 'API_ERROR')
        message (str): User-friendly error message
        details (str, optional): Technical details for logging
        
    Returns:
        dict: Structured error response
    """
    return {
        'error': {
            'type': error_type,
            'message': message,
            'details': details,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    }
