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
# DATA STORAGE CONFIGURATION
# ============================================================================

# Storage type: 'csv' or 'sqlite'
# CSV: Simple, human-readable files (good for beginners)
# SQLite: Database format (better for large datasets and queries)
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'csv')  # Options: 'csv', 'sqlite'

# Storage directory for data files
STORAGE_DIR = os.getenv('STORAGE_DIR', 'weather_data')

# CSV Configuration
CSV_FILE = 'weather_data.csv'
CSV_COLUMNS = ['datetime', 'city', 'temperature', 'humidity', 'condition', 'units']

# SQLite Configuration
SQLITE_DB = 'weather_data.db'

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================

FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
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
ALERT_TEMP_HIGH_CELSIUS = 35       # High temperature alert in Celsius
ALERT_TEMP_HIGH_FAHRENHEIT = 95    # High temperature alert in Fahrenheit
ALERT_TEMP_LOW_CELSIUS = 0         # Freezing temperature alert in Celsius
ALERT_TEMP_LOW_FAHRENHEIT = 32     # Freezing temperature alert in Fahrenheit

# Humidity threshold (percentage)
ALERT_HUMIDITY_HIGH = 80  # High humidity alert at 80% or above

# Wind speed thresholds
ALERT_WIND_HIGH_METRIC = 20        # High wind alert in m/s (metric)
ALERT_WIND_HIGH_IMPERIAL = 45      # High wind alert in mph (imperial)

# Bad weather conditions (any of these will trigger an alert)
BAD_WEATHER_CONDITIONS = [
    'Thunderstorm',
    'Tornado',
    'Hurricane',
    'Extreme',
    'Severe',
    'Rainy',
    'Rain',
    'Drizzle',
    'Snow',
    'Blizzard',
    'Hail',
    'Sleet',
    'Freezing'
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
