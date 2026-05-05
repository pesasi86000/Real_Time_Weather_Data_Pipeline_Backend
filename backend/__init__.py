"""
Weather Backend API Package
A simple, beginner-friendly real-time weather data pipeline backend
"""

__version__ = '1.0.0'
__author__ = 'Your Name'
__description__ = 'Real-time weather data pipeline backend with Flask API and CSV storage'

# Import main components for easy access
from .app import app
from .weather_service import fetch_weather_data, validate_city
from .csv_service import save_weather_to_csv
from .config import *
from .helpers import setup_logger, error_response, success_response

__all__ = [
    'app',
    'fetch_weather_data',
    'validate_city',
    'save_weather_to_csv',
    'setup_logger',
    'error_response',
    'success_response',
]
