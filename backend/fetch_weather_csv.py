import requests
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
CSV_FILE = 'weather_data.csv'
CSV_COLUMNS = ['datetime', 'city', 'temperature', 'humidity', 'condition']


def fetch_weather(city):
    """
    Fetch current weather data for a city from OpenWeather API
    
    Args:
        city (str): City name
        
    Returns:
        dict: Weather data or None if request fails
    """
    try:
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'  # Use Celsius
        }
        
        response = requests.get(OPENWEATHER_BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract required fields
        weather_record = {
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'city': data.get('name', city),
            'temperature': round(data['main']['temp'], 2),
            'humidity': data['main']['humidity'],
            'condition': data['weather'][0]['main']
        }
        
        logger.info(f"Successfully fetched weather for {city}")
        return weather_record
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {city}: {str(e)}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing weather data for {city}: {str(e)}")
        return None


def file_has_header():
    """Check if CSV file exists and has header row"""
    return os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0


def save_weather_to_csv(weather_records):
    """
    Save weather records to CSV file, appending if file already exists
    
    Args:
        weather_records (list): List of weather record dictionaries
    """
    if not weather_records:
        logger.warning("No weather records to save")
        return
    
    try:
        file_exists = os.path.exists(CSV_FILE)
        has_header = file_has_header()
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
            
            # Write header only if file is new or empty
            if not has_header:
                writer.writeheader()
                logger.info(f"Created new CSV file: {CSV_FILE}")
            
            # Write weather records
            writer.writerows(weather_records)
            logger.info(f"Saved {len(weather_records)} record(s) to {CSV_FILE}")
            
    except IOError as e:
        logger.error(f"Error writing to CSV file: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error saving to CSV: {str(e)}")


def main(cities=None):
    """
    Main function to fetch weather for cities and save to CSV
    
    Args:
        cities (list): List of city names. If None, uses default cities.
    """
    if not OPENWEATHER_API_KEY:
        logger.error("OPENWEATHER_API_KEY environment variable not set")
        return
    
    # Default cities if none provided
    if cities is None:
        cities = ['London', 'New York', 'Tokyo', 'Paris', 'Sydney']
    
    logger.info(f"Fetching weather for {len(cities)} city/cities")
    
    weather_records = []
    for city in cities:
        weather_data = fetch_weather(city)
        if weather_data:
            weather_records.append(weather_data)
    
    if weather_records:
        save_weather_to_csv(weather_records)
        logger.info("Weather data fetch completed successfully")
    else:
        logger.warning("No weather data was retrieved")


if __name__ == '__main__':
    # Example: Fetch weather for specific cities
    main(cities=['London', 'New York', 'Tokyo'])
    
    # Or fetch for default cities:
    # main()
