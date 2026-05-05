"""
Data Storage Module
Handles historical weather data storage for CSV and SQLite formats.
Supports append-only operations to preserve historical data.
"""

import csv
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from helpers import setup_logger
from config import STORAGE_TYPE, CSV_FILE, SQLITE_DB, CSV_COLUMNS, STORAGE_DIR

logger = setup_logger(__name__)


# ============================================================================
# INITIALIZATION HELPERS
# ============================================================================

def initialize_storage():
    """
    Initialize storage directory and files/database based on configured storage type.
    Creates directories and tables/headers as needed.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Create storage directory if it doesn't exist
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
            logger.info(f"Created storage directory: {STORAGE_DIR}")
        
        # Initialize based on storage type
        if STORAGE_TYPE == 'sqlite':
            success, msg = initialize_sqlite()
        elif STORAGE_TYPE == 'csv':
            success, msg = initialize_csv()
        else:
            return False, f"Unknown storage type: {STORAGE_TYPE}"
        
        if success:
            logger.info(f"Storage initialized successfully ({STORAGE_TYPE})")
        return success, msg
        
    except Exception as e:
        logger.error(f"Error initializing storage: {str(e)}")
        return False, f"Storage initialization error: {str(e)}"


def initialize_csv():
    """
    Initialize CSV file with headers if it doesn't exist.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        csv_path = os.path.join(STORAGE_DIR, CSV_FILE)
        
        if os.path.exists(csv_path):
            logger.debug(f"CSV file already exists: {csv_path}")
            return True, "CSV file already exists"
        
        # Create new CSV with headers
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        
        logger.info(f"Created CSV file with headers: {csv_path}")
        return True, f"CSV file created at {csv_path}"
        
    except Exception as e:
        logger.error(f"Error initializing CSV: {str(e)}")
        return False, f"CSV initialization error: {str(e)}"


def initialize_sqlite():
    """
    Initialize SQLite database and create weather_data table if it doesn't exist.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        db_path = os.path.join(STORAGE_DIR, SQLITE_DB)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT NOT NULL,
                city TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity INTEGER NOT NULL,
                condition TEXT NOT NULL,
                units TEXT DEFAULT 'metric',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index on datetime and city for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_datetime 
            ON weather_data(datetime)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_city 
            ON weather_data(city)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"SQLite database initialized: {db_path}")
        return True, f"SQLite database created at {db_path}"
        
    except Exception as e:
        logger.error(f"Error initializing SQLite: {str(e)}")
        return False, f"SQLite initialization error: {str(e)}"


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_weather_record(weather_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate weather data record has all required fields.
    
    Args:
        weather_data (dict): Weather data to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    required_fields = ['city', 'temperature', 'humidity', 'condition']
    
    if not isinstance(weather_data, dict):
        return False, "Weather data must be a dictionary"
    
    for field in required_fields:
        if field not in weather_data:
            return False, f"Missing required field: {field}"
    
    # Validate data types
    try:
        float(weather_data['temperature'])
        int(weather_data['humidity'])
    except (ValueError, TypeError):
        return False, "Temperature must be numeric and humidity must be integer"
    
    if weather_data['humidity'] < 0 or weather_data['humidity'] > 100:
        return False, "Humidity must be between 0 and 100"
    
    return True, None


def format_weather_record(weather_data: Dict) -> Dict:
    """
    Convert weather data to standard storage format.
    
    Args:
        weather_data (dict): Raw weather data from API
        
    Returns:
        dict: Formatted record with standardized fields
        
    Raises:
        ValueError: If required fields are missing
    """
    is_valid, error = validate_weather_record(weather_data)
    if not is_valid:
        logger.error(f"Invalid weather record: {error}")
        raise ValueError(error)
    
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
# STORAGE OPERATIONS (CSV)
# ============================================================================

def save_to_csv(weather_data: Dict) -> Tuple[bool, str]:
    """
    Save a single weather record to CSV file (append mode).
    Creates file with headers if it doesn't exist.
    
    Args:
        weather_data (dict): Weather data to save
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validate and format the record
        record = format_weather_record(weather_data)
        
        csv_path = os.path.join(STORAGE_DIR, CSV_FILE)
        
        # Check if file exists and has content
        file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        
        # If file doesn't exist, create with headers
        if not file_exists:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerow(record)
            logger.info(f"Created CSV file and saved weather data for {record['city']}")
        else:
            # Append to existing file
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
                writer.writerow(record)
            logger.info(f"Appended weather data for {record['city']} to CSV")
        
        return True, f"Weather data saved to CSV for {record['city']}"
        
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")
        return False, f"CSV save error: {str(e)}"


def save_batch_to_csv(weather_records: List[Dict]) -> Tuple[bool, str]:
    """
    Save multiple weather records to CSV file in batch.
    
    Args:
        weather_records (list): List of weather data dictionaries
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not weather_records:
            return False, "No records to save"
        
        # Validate and format all records
        formatted_records = []
        for record in weather_records:
            try:
                formatted = format_weather_record(record)
                formatted_records.append(formatted)
            except ValueError as e:
                logger.warning(f"Skipping invalid record: {str(e)}")
                continue
        
        if not formatted_records:
            return False, "No valid records to save"
        
        csv_path = os.path.join(STORAGE_DIR, CSV_FILE)
        
        # Check if file exists and has content
        file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        
        # If file doesn't exist, create with headers
        if not file_exists:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerows(formatted_records)
            logger.info(f"Created CSV file and saved {len(formatted_records)} records")
        else:
            # Append to existing file
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
                writer.writerows(formatted_records)
            logger.info(f"Appended {len(formatted_records)} records to CSV")
        
        return True, f"Saved {len(formatted_records)} records to CSV"
        
    except Exception as e:
        logger.error(f"Error saving batch to CSV: {str(e)}")
        return False, f"Batch CSV save error: {str(e)}"


# ============================================================================
# STORAGE OPERATIONS (SQLite)
# ============================================================================

def save_to_sqlite(weather_data: Dict) -> Tuple[bool, str]:
    """
    Save a single weather record to SQLite database.
    
    Args:
        weather_data (dict): Weather data to save
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validate and format the record
        record = format_weather_record(weather_data)
        
        db_path = os.path.join(STORAGE_DIR, SQLITE_DB)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weather_data 
            (datetime, city, temperature, humidity, condition, units)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            record['datetime'],
            record['city'],
            record['temperature'],
            record['humidity'],
            record['condition'],
            record['units']
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved weather data for {record['city']} to SQLite")
        return True, f"Weather data saved to SQLite for {record['city']}"
        
    except Exception as e:
        logger.error(f"Error saving to SQLite: {str(e)}")
        return False, f"SQLite save error: {str(e)}"


def save_batch_to_sqlite(weather_records: List[Dict]) -> Tuple[bool, str]:
    """
    Save multiple weather records to SQLite database in batch.
    
    Args:
        weather_records (list): List of weather data dictionaries
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not weather_records:
            return False, "No records to save"
        
        # Validate and format all records
        formatted_records = []
        for record in weather_records:
            try:
                formatted = format_weather_record(record)
                formatted_records.append(formatted)
            except ValueError as e:
                logger.warning(f"Skipping invalid record: {str(e)}")
                continue
        
        if not formatted_records:
            return False, "No valid records to save"
        
        db_path = os.path.join(STORAGE_DIR, SQLITE_DB)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for record in formatted_records:
            cursor.execute('''
                INSERT INTO weather_data 
                (datetime, city, temperature, humidity, condition, units)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record['datetime'],
                record['city'],
                record['temperature'],
                record['humidity'],
                record['condition'],
                record['units']
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {len(formatted_records)} records to SQLite")
        return True, f"Saved {len(formatted_records)} records to SQLite"
        
    except Exception as e:
        logger.error(f"Error saving batch to SQLite: {str(e)}")
        return False, f"Batch SQLite save error: {str(e)}"


# ============================================================================
# UNIFIED STORAGE INTERFACE
# ============================================================================

def save_weather_data(weather_data: Dict) -> Tuple[bool, str]:
    """
    Save weather data using configured storage type.
    Automatically calls appropriate storage method (CSV or SQLite).
    
    Args:
        weather_data (dict): Weather data to save
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if STORAGE_TYPE == 'sqlite':
        return save_to_sqlite(weather_data)
    elif STORAGE_TYPE == 'csv':
        return save_to_csv(weather_data)
    else:
        logger.error(f"Unknown storage type: {STORAGE_TYPE}")
        return False, f"Unknown storage type: {STORAGE_TYPE}"


def save_weather_batch(weather_records: List[Dict]) -> Tuple[bool, str]:
    """
    Save multiple weather records using configured storage type.
    
    Args:
        weather_records (list): List of weather data dictionaries
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if STORAGE_TYPE == 'sqlite':
        return save_batch_to_sqlite(weather_records)
    elif STORAGE_TYPE == 'csv':
        return save_batch_to_csv(weather_records)
    else:
        logger.error(f"Unknown storage type: {STORAGE_TYPE}")
        return False, f"Unknown storage type: {STORAGE_TYPE}"


# ============================================================================
# RETRIEVAL OPERATIONS
# ============================================================================

def get_weather_data_csv(city: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Retrieve weather records from CSV file.
    
    Args:
        city (str, optional): Filter by city name. If None, returns all records.
        limit (int): Maximum number of records to return. Default 100.
        
    Returns:
        list: List of weather record dictionaries
    """
    try:
        csv_path = os.path.join(STORAGE_DIR, CSV_FILE)
        
        if not os.path.exists(csv_path):
            logger.warning(f"CSV file not found: {csv_path}")
            return []
        
        records = []
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if city is None or row['city'].lower() == city.lower():
                    records.append(row)
                if len(records) >= limit:
                    break
        
        logger.info(f"Retrieved {len(records)} records from CSV")
        return records
        
    except Exception as e:
        logger.error(f"Error retrieving data from CSV: {str(e)}")
        return []


def get_weather_data_sqlite(city: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Retrieve weather records from SQLite database.
    
    Args:
        city (str, optional): Filter by city name. If None, returns all records.
        limit (int): Maximum number of records to return. Default 100.
        
    Returns:
        list: List of weather record dictionaries
    """
    try:
        db_path = os.path.join(STORAGE_DIR, SQLITE_DB)
        
        if not os.path.exists(db_path):
            logger.warning(f"SQLite database not found: {db_path}")
            return []
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        if city:
            cursor.execute('''
                SELECT datetime, city, temperature, humidity, condition, units
                FROM weather_data
                WHERE city = ?
                ORDER BY datetime DESC
                LIMIT ?
            ''', (city, limit))
        else:
            cursor.execute('''
                SELECT datetime, city, temperature, humidity, condition, units
                FROM weather_data
                ORDER BY datetime DESC
                LIMIT ?
            ''', (limit,))
        
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"Retrieved {len(records)} records from SQLite")
        return records
        
    except Exception as e:
        logger.error(f"Error retrieving data from SQLite: {str(e)}")
        return []


def get_weather_data(city: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Retrieve weather records using configured storage type.
    
    Args:
        city (str, optional): Filter by city name. If None, returns all records.
        limit (int): Maximum number of records to return. Default 100.
        
    Returns:
        list: List of weather record dictionaries
    """
    if STORAGE_TYPE == 'sqlite':
        return get_weather_data_sqlite(city, limit)
    elif STORAGE_TYPE == 'csv':
        return get_weather_data_csv(city, limit)
    else:
        logger.error(f"Unknown storage type: {STORAGE_TYPE}")
        return []


def get_storage_stats() -> Dict:
    """
    Get statistics about stored data.
    
    Returns:
        dict: Statistics including record count, storage size, etc.
    """
    try:
        stats = {
            'storage_type': STORAGE_TYPE,
            'storage_dir': STORAGE_DIR,
            'record_count': 0,
            'file_size_mb': 0
        }
        
        if STORAGE_TYPE == 'csv':
            csv_path = os.path.join(STORAGE_DIR, CSV_FILE)
            if os.path.exists(csv_path):
                stats['file_size_mb'] = round(os.path.getsize(csv_path) / (1024 * 1024), 2)
                # Count records (excluding header)
                with open(csv_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    stats['record_count'] = sum(1 for _ in reader)
        
        elif STORAGE_TYPE == 'sqlite':
            db_path = os.path.join(STORAGE_DIR, SQLITE_DB)
            if os.path.exists(db_path):
                stats['file_size_mb'] = round(os.path.getsize(db_path) / (1024 * 1024), 2)
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM weather_data')
                stats['record_count'] = cursor.fetchone()[0]
                conn.close()
        
        logger.info(f"Storage stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {str(e)}")
        return {'error': str(e)}


# ============================================================================
# EXPORT HELPERS
# ============================================================================

def export_to_csv_from_sqlite(output_path: str) -> Tuple[bool, str]:
    """
    Export all SQLite data to a CSV file (useful for data portability).
    
    Args:
        output_path (str): Path where to save the CSV export
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if STORAGE_TYPE != 'sqlite':
            return False, "Export only works when using SQLite storage"
        
        records = get_weather_data_sqlite()
        
        if not records:
            return False, "No data to export"
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            
            for record in records:
                # Filter to only CSV columns
                filtered = {k: record.get(k) for k in CSV_COLUMNS}
                writer.writerow(filtered)
        
        logger.info(f"Exported {len(records)} records to CSV: {output_path}")
        return True, f"Exported {len(records)} records to {output_path}"
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        return False, f"Export error: {str(e)}"
