"""
Fetch Weather Data and Save to CSV
Standalone script to fetch weather for multiple cities and save to CSV
"""

import logging
from weather_service import fetch_weather_data
from csv_service import save_weather_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_and_save_weather(cities, units='metric'):
    """
    Fetch weather for multiple cities and save to CSV
    
    This function orchestrates the weather fetching and CSV saving process.
    
    Args:
        cities (list): List of city names to fetch weather for
        units (str): Temperature units - 'metric' (Celsius) or 'imperial' (Fahrenheit)
        
    Returns:
        tuple: (success: bool, summary: str)
        - On success: (True, success message with count)
        - On failure: (False, error message)
        
    Example:
        >>> success, message = fetch_and_save_weather(['London', 'Paris', 'Tokyo'])
        >>> if success:
        ...     print(f"✓ {message}")
    """
    if not cities:
        logger.warning("No cities provided")
        return False, "No cities to fetch"
    
    # Fetch weather for each city
    weather_records = []
    successful_cities = []
    failed_cities = []
    
    for city in cities:
        success, result = fetch_weather_data(city, units)
        
        if success:
            weather_records.append(result)
            successful_cities.append(city)
            logger.info(f"✓ Fetched weather for {city}")
        else:
            failed_cities.append((city, result))
            logger.error(f"✗ Failed to fetch weather for {city}: {result}")
    
    # Log summary of fetched cities
    if successful_cities:
        logger.info(f"Successfully fetched weather for: {', '.join(successful_cities)}")
    
    if failed_cities:
        failed_summary = '; '.join([f"{city} ({error})" for city, error in failed_cities])
        logger.warning(f"Failed to fetch weather for: {failed_summary}")
    
    # If no weather data was collected, return failure
    if not weather_records:
        logger.error("No weather data collected from any city")
        return False, "Failed to fetch weather data for any city"
    
    # Save to CSV
    success, message = save_weather_to_csv(weather_records)
    
    if success:
        logger.info(f"✓ {message}")
        return True, f"Successfully fetched and saved weather for {len(weather_records)} city/cities"
    else:
        logger.error(f"✗ {message}")
        return False, message


def main(cities=None):
    """
    Main entry point for the weather fetch and CSV save script
    
    Args:
        cities (list, optional): List of city names. If None, uses default cities.
    """
    # Default cities if none provided
    if cities is None:
        cities = ['London', 'New York', 'Tokyo', 'Paris', 'Sydney']
    
    logger.info(f"Starting weather fetch for {len(cities)} city/cities...")
    
    # Fetch and save weather
    success, message = fetch_and_save_weather(cities, units='metric')
    
    if success:
        logger.info(f"✓ {message}")
    else:
        logger.error(f"✗ {message}")


if __name__ == '__main__':
    # Example: Fetch weather for specific cities
    main(cities=['London', 'New York', 'Tokyo'])
    
    # Or fetch for default cities:
    # main()
