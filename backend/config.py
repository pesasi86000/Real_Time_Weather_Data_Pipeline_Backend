"""
Configuration Module
Centralized configuration for the weather backend application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# API CONFIGURATION
# ============================================================================

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
REQUEST_TIMEOUT = 5  # seconds

# ============================================================================
# CSV CONFIGURATION
# ============================================================================

CSV_FILE = 'weather_data.csv'
CSV_COLUMNS = ['datetime', 'city', 'temperature', 'humidity', 'condition', 'units']

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================

FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', True)
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

# ============================================================================
# API LIMITS
# ============================================================================

MAX_BATCH_CITIES = 50  # Maximum number of cities per batch request
MIN_CITY_LENGTH = 2
MAX_CITY_LENGTH = 100

# ============================================================================
# VALID UNITS
# ============================================================================

VALID_UNITS = ['metric', 'imperial']
DEFAULT_UNITS = 'metric'

# ============================================================================
# WEATHER ALERT THRESHOLDS
# ============================================================================

# Temperature thresholds (in the respective units)
ALERT_TEMP_HIGH_CELSIUS = 35  # High temperature alert in Celsius
ALERT_TEMP_HIGH_FAHRENHEIT = 95  # High temperature alert in Fahrenheit

# Humidity threshold (percentage)
ALERT_HUMIDITY_HIGH = 80  # High humidity alert at 80% or above

# Bad weather conditions (any of these will trigger an alert)
BAD_WEATHER_CONDITIONS = [
    'Thunderstorm',
    'Tornado',
    'Hurricane',
    'Extreme',
    'Severe',
    'Rainy',
    'Rain',
    'Drizzle'
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
