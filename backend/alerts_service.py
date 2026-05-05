"""
Alerts Service Module
Handles weather alert generation based on configurable thresholds
"""

from helpers import setup_logger
from config import (
    ALERT_TEMP_HIGH_CELSIUS,
    ALERT_TEMP_HIGH_FAHRENHEIT,
    ALERT_HUMIDITY_HIGH,
    BAD_WEATHER_CONDITIONS
)

logger = setup_logger(__name__)


def check_temperature_alert(temperature, units):
    """
    Check if temperature exceeds the alert threshold
    
    Args:
        temperature (float): Current temperature
        units (str): Temperature units ('metric' or 'imperial')
        
    Returns:
        dict: Alert info with 'active' and 'message' keys, or None if no alert
    """
    threshold = ALERT_TEMP_HIGH_CELSIUS if units == 'metric' else ALERT_TEMP_HIGH_FAHRENHEIT
    unit_symbol = '°C' if units == 'metric' else '°F'
    
    if temperature >= threshold:
        return {
            'type': 'HIGH_TEMPERATURE',
            'active': True,
            'message': f'High temperature alert: {temperature}{unit_symbol} (threshold: {threshold}{unit_symbol})',
            'severity': 'warning'
        }
    
    return None


def check_humidity_alert(humidity):
    """
    Check if humidity exceeds the alert threshold
    
    Args:
        humidity (int): Current humidity percentage (0-100)
        
    Returns:
        dict: Alert info with 'active' and 'message' keys, or None if no alert
    """
    if humidity >= ALERT_HUMIDITY_HIGH:
        return {
            'type': 'HIGH_HUMIDITY',
            'active': True,
            'message': f'High humidity alert: {humidity}% (threshold: {ALERT_HUMIDITY_HIGH}%)',
            'severity': 'warning'
        }
    
    return None


def check_bad_weather_alert(condition, description):
    """
    Check if current weather condition is considered "bad"
    
    Args:
        condition (str): Weather condition (e.g., 'Rain', 'Thunderstorm')
        description (str): Weather description (e.g., 'light rain')
        
    Returns:
        dict: Alert info with 'active' and 'message' keys, or None if no alert
    """
    # Check if condition matches any bad weather condition (case-insensitive)
    for bad_condition in BAD_WEATHER_CONDITIONS:
        if bad_condition.lower() in condition.lower() or bad_condition.lower() in description.lower():
            severity = 'critical' if condition.lower() in ['thunderstorm', 'tornado', 'hurricane', 'extreme'] else 'warning'
            
            return {
                'type': 'BAD_WEATHER',
                'active': True,
                'message': f'Bad weather alert: {condition} - {description}',
                'severity': severity
            }
    
    return None


def generate_alerts(weather_data):
    """
    Generate all applicable weather alerts for the given weather data
    
    Args:
        weather_data (dict): Weather information containing temperature, humidity, 
                            condition, description, and units
        
    Returns:
        dict: Alerts dictionary with 'alerts_active' bool and 'alerts' list
        
    Example return:
        {
            'alerts_active': True,
            'alerts': [
                {
                    'type': 'HIGH_TEMPERATURE',
                    'active': True,
                    'message': 'High temperature alert: 38°C (threshold: 35°C)',
                    'severity': 'warning'
                },
                ...
            ]
        }
    """
    alerts = []
    
    # Check temperature alert
    temp_alert = check_temperature_alert(weather_data['temperature'], weather_data['units'])
    if temp_alert:
        alerts.append(temp_alert)
        logger.warning(f"{weather_data['city']}: {temp_alert['message']}")
    
    # Check humidity alert
    humidity_alert = check_humidity_alert(weather_data['humidity'])
    if humidity_alert:
        alerts.append(humidity_alert)
        logger.warning(f"{weather_data['city']}: {humidity_alert['message']}")
    
    # Check bad weather alert
    weather_alert = check_bad_weather_alert(weather_data['condition'], weather_data['description'])
    if weather_alert:
        alerts.append(weather_alert)
        logger.warning(f"{weather_data['city']}: {weather_alert['message']}")
    
    return {
        'alerts_active': len(alerts) > 0,
        'alerts': alerts
    }
