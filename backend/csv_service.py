"""
CSV Service Module
Handles all CSV file operations with clean, modular functions
"""

import csv
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
CSV_FILE = 'weather_data.csv'
CSV_COLUMNS = ['datetime', 'city', 'temperature', 'humidity', 'condition', 'units']


# ============================================================================
# FILE CHECKING HELPERS
# ============================================================================

def csv_file_exists():
    """
    Check if CSV file already exists
    
    Returns:
        bool: True if file exists, False otherwise
    """
    return os.path.exists(CSV_FILE)


def csv_has_header():
    """
    Check if CSV file exists and has content (header row)
    
    Returns:
        bool: True if file exists and has content, False otherwise
    """
    if not csv_file_exists():
        return False
    return os.path.getsize(CSV_FILE) > 0


def get_csv_file_path():
    """
    Get the full absolute path to the CSV file
    
    Returns:
        str: Absolute path to the CSV file
    """
    return os.path.abspath(CSV_FILE)


# ============================================================================
# DATA FORMATTING HELPERS
# ============================================================================

def validate_weather_record(weather_data):
    """
    Validate that weather record has required fields
    
    Args:
        weather_data (dict): Weather data from API
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    required_fields = ['city', 'temperature', 'humidity', 'condition']
    
    if not isinstance(weather_data, dict):
        return False, "Weather data must be a dictionary"
    
    for field in required_fields:
        if field not in weather_data:
            return False, f"Missing required field: {field}"
    
    return True, None


def format_weather_record(weather_data):
    """
    Convert weather API response to CSV record format
    
    Extracts relevant fields from weather API response and formats them
    as a dictionary suitable for CSV writing.
    
    Args:
        weather_data (dict): Weather data from API with required fields
        
    Returns:
        dict: Formatted record ready for CSV export
        
    Raises:
        ValueError: If weather_data is missing required fields
        
    Example:
        >>> weather = {'city': 'London', 'temperature': 15.5, 'humidity': 70, 'condition': 'Rainy', 'units': 'metric'}
        >>> record = format_weather_record(weather)
        >>> record['temperature']
        15.5
    """
    # Validate the record first
    is_valid, error = validate_weather_record(weather_data)
    if not is_valid:
        logger.error(f"Invalid weather record: {error}")
        raise ValueError(error)
    
    # Format the record
    record = {
        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'city': str(weather_data.get('city', 'Unknown')).strip(),
        'temperature': round(float(weather_data.get('temperature', 0)), 2),
        'humidity': int(weather_data.get('humidity', 0)),
        'condition': str(weather_data.get('condition', 'Unknown')).strip(),
        'units': str(weather_data.get('units', 'metric')).lower()
    }
    
    return record


# ============================================================================
# CSV WRITING HELPERS
# ============================================================================

def write_csv_header():
    """
    Write header row to CSV file
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        logger.info(f"Created new CSV file with header: {CSV_FILE}")
        return True, "CSV file created"
    except IOError as e:
        logger.error(f"Error creating CSV file: {str(e)}")
        return False, f"Error creating CSV file: {str(e)}"


def append_csv_records(csv_records):
    """
    Append records to CSV file
    
    Args:
        csv_records (list): List of formatted record dictionaries
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
            writer.writerows(csv_records)
        logger.info(f"Appended {len(csv_records)} record(s) to {CSV_FILE}")
        return True, f"Saved {len(csv_records)} record(s)"
    except IOError as e:
        logger.error(f"Error writing to CSV file: {str(e)}")
        return False, f"Error writing to CSV: {str(e)}"


# ============================================================================
# MAIN PUBLIC FUNCTION
# ============================================================================

def save_weather_to_csv(weather_records):
    """
    Save weather records to CSV file
    
    Handles creating a new CSV file with headers if it doesn't exist,
    or appends records to an existing file. Each record is validated
    and formatted before being written.
    
    Args:
        weather_records (list): List of weather dictionaries from API
        
    Returns:
        tuple: (success: bool, message: str)
        - On success: (True, success message with count)
        - On failure: (False, error message)
        
    Example:
        >>> records = [{'city': 'London', 'temperature': 15, 'humidity': 70, 'condition': 'Rainy', 'units': 'metric'}]
        >>> success, message = save_weather_to_csv(records)
        >>> if success:
        ...     print(f"Saved successfully: {message}")
    """
    
    # Validate input
    if not weather_records:
        logger.warning("No weather records to save")
        return False, "No records provided"
    
    if not isinstance(weather_records, list):
        logger.error("Weather records must be a list")
        return False, "Records must be a list"
    
    try:
        # Format and validate all records
        csv_records = []
        for idx, record in enumerate(weather_records):
            try:
                formatted_record = format_weather_record(record)
                csv_records.append(formatted_record)
            except ValueError as e:
                logger.warning(f"Skipping invalid record #{idx}: {str(e)}")
                continue
        
        # If no valid records after formatting, return failure
        if not csv_records:
            logger.error("No valid weather records to save")
            return False, "No valid records to save"
        
        # Check if we need to write header
        needs_header = not csv_has_header()
        
        # Create or append to CSV
        if needs_header:
            success, message = write_csv_header()
            if not success:
                return False, message
        
        # Append records
        success, message = append_csv_records(csv_records)
        return success, message
        
    except Exception as e:
        logger.error(f"Unexpected error saving to CSV: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def get_csv_record_count():
    """Get the number of records in the CSV file (excluding header)"""
    if not csv_file_exists():
        return 0
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # Skip header row
            next(reader, None)
            # Count remaining rows
            return sum(1 for _ in reader)
    except Exception as e:
        logger.error(f"Error counting CSV records: {str(e)}")
        return 0
