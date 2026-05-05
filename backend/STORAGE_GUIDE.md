# Data Storage Guide

## Overview

The weather backend now includes a comprehensive data storage system that saves historical weather data without overwriting existing records. The system supports both **CSV** and **SQLite** formats, making it easy to store and retrieve weather information for analysis and frontend visualization.

---

## Storage Types

### CSV Storage
- **Best for**: Beginners, small datasets, spreadsheet analysis
- **Pros**: 
  - Human-readable format
  - Easy to open in Excel or Google Sheets
  - Simple to understand and debug
  - Good for quick exports
- **Cons**: 
  - Slower queries on large datasets
  - Limited data type support
  - Can become large with many records

**Use CSV if:** You're new to databases and want simplicity.

### SQLite Storage
- **Best for**: Production use, large datasets, frequent queries
- **Pros**:
  - Fast queries with indexing
  - Efficient storage
  - Built-in data validation
  - Supports complex queries
  - No additional setup required (SQLite comes with Python)
- **Cons**:
  - Less human-readable
  - Requires SQLite tools to view directly

**Use SQLite if:** You plan to grow your data or need efficient queries.

---

## Configuration

### Setting Storage Type

Edit the storage type in `config.py`:

```python
# Option 1: CSV Storage
STORAGE_TYPE = 'csv'

# Option 2: SQLite Storage
STORAGE_TYPE = 'sqlite'

# Storage directory (where files/database are saved)
STORAGE_DIR = 'weather_data'
```

Or set via environment variable:

```bash
# In .env file
STORAGE_TYPE=sqlite
STORAGE_DIR=weather_data
```

---

## Quick Start

### 1. Initialize Storage

Before saving data for the first time, initialize storage:

```python
from data_storage import initialize_storage

success, message = initialize_storage()
print(message)
# Output: "Storage initialized successfully (csv)"
#         or "Storage initialized successfully (sqlite)"
```

### 2. Save Single Weather Record

```python
from data_storage import save_weather_data

weather = {
    'city': 'London',
    'temperature': 15.5,
    'humidity': 72,
    'condition': 'Rainy',
    'units': 'metric'
}

success, message = save_weather_data(weather)
print(message)
# Output: "Weather data saved to CSV for London"
```

### 3. Save Multiple Records (Batch)

```python
from data_storage import save_weather_batch

weather_records = [
    {
        'city': 'London',
        'temperature': 15.5,
        'humidity': 72,
        'condition': 'Rainy',
        'units': 'metric'
    },
    {
        'city': 'Paris',
        'temperature': 18.2,
        'humidity': 65,
        'condition': 'Cloudy',
        'units': 'metric'
    },
    {
        'city': 'Tokyo',
        'temperature': 22.1,
        'humidity': 68,
        'condition': 'Sunny',
        'units': 'metric'
    }
]

success, message = save_weather_batch(weather_records)
print(message)
# Output: "Saved 3 records to CSV"
```

### 4. Retrieve Historical Data

```python
from data_storage import get_weather_data

# Get all data (last 100 records)
all_records = get_weather_data()

# Get data for specific city (last 100 records)
london_data = get_weather_data(city='London', limit=50)

# Print results
for record in london_data:
    print(f"{record['datetime']} - {record['city']}: {record['temperature']}°C, {record['condition']}")
```

### 5. Check Storage Statistics

```python
from data_storage import get_storage_stats

stats = get_storage_stats()
print(f"Storage Type: {stats['storage_type']}")
print(f"Total Records: {stats['record_count']}")
print(f"File Size: {stats['file_size_mb']} MB")

# Output:
# Storage Type: csv
# Total Records: 248
# File Size: 0.05 MB
```

---

## Integration with Existing Code

### With Weather Scheduler

The scheduler can automatically save data when collecting weather:

```python
# In weather_scheduler.py
from data_storage import save_weather_batch, initialize_storage

# Initialize storage once at startup
initialize_storage()

# In your collection loop
weather_records = fetch_weather_for_cities(cities)
success, message = save_weather_batch(weather_records)
logger.info(message)
```

### With Flask API Endpoint

Add an endpoint to retrieve historical data:

```python
# In app.py
from data_storage import get_weather_data

@app.route('/weather/history', methods=['GET'])
def get_weather_history():
    """
    Get historical weather data for a city
    
    Query parameters:
        - city (optional): Filter by city name
        - limit (optional): Maximum records to return (default 100)
    """
    try:
        city = request.args.get('city', None)
        limit = request.args.get('limit', 100, type=int)
        
        records = get_weather_data(city=city, limit=limit)
        
        if not records:
            return error_response(False, 'No data found', 
                                'No weather history available', 404)
        
        return success_response({
            'city': city or 'All Cities',
            'records_count': len(records),
            'data': records
        }, 200)
        
    except Exception as e:
        logger.exception(f"Error retrieving weather history: {str(e)}")
        return error_response(False, 'Server error', str(e), 500)
```

---

## Data Format

### CSV Format

The CSV file contains the following columns:

| Column | Type | Example |
|--------|------|---------|
| datetime | String | 2025-05-01 14:30:45 |
| city | String | London |
| temperature | Float | 15.5 |
| humidity | Integer | 72 |
| condition | String | Rainy |
| units | String | metric |

**Sample CSV Content:**
```csv
datetime,city,temperature,humidity,condition,units
2025-05-01 14:30:45,London,15.5,72,Rainy,metric
2025-05-01 14:30:46,Paris,18.2,65,Cloudy,metric
2025-05-01 14:35:12,London,15.5,72,Rainy,metric
```

### SQLite Format

The SQLite database has a single `weather_data` table with:

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Auto-incrementing primary key |
| datetime | TEXT | ISO format timestamp |
| city | TEXT | City name |
| temperature | REAL | Numeric temperature value |
| humidity | INTEGER | 0-100 percentage |
| condition | TEXT | Weather condition |
| units | TEXT | 'metric' or 'imperial' |
| created_at | TIMESTAMP | Auto-recorded insertion time |

**Indexes:** `weather_data` table has indexes on `datetime` and `city` for fast queries.

---

## File Locations

### CSV Files
```
backend/
└── weather_data/
    └── weather_data.csv  (human-readable, can open in Excel)
```

### SQLite Files
```
backend/
└── weather_data/
    └── weather_data.db  (binary database file)
```

---

## Common Use Cases

### Use Case 1: View All Weather Data for a City

```python
from data_storage import get_weather_data

london_history = get_weather_data(city='London', limit=500)

for record in london_history:
    print(f"{record['datetime']}: {record['temperature']}°C, {record['humidity']}%, {record['condition']}")
```

### Use Case 2: Export SQLite Data to CSV

```python
from data_storage import export_to_csv_from_sqlite

success, message = export_to_csv_from_sqlite('weather_export.csv')
print(message)
# Output: "Exported 248 records to weather_export.csv"
```

**Use this** to share data with non-technical users or import into Excel.

### Use Case 3: Collect Data Every 5 Minutes and Save

```python
# This is already built into weather_scheduler.py
# It automatically collects and saves data:

from weather_scheduler import run_scheduler

run_scheduler()  # Runs every 5 minutes, collecting and saving data
```

### Use Case 4: Display Data on Frontend

```python
# API endpoint to get data for dashboard visualization
from flask import jsonify
from data_storage import get_weather_data

@app.route('/api/weather/chart-data', methods=['GET'])
def get_chart_data():
    """Get data for frontend chart/graph visualization"""
    city = request.args.get('city', 'London')
    records = get_weather_data(city=city, limit=288)  # Last 24 hours at 5-min intervals
    
    # Format for frontend charts (e.g., Chart.js, D3.js)
    chart_data = {
        'labels': [r['datetime'] for r in records],
        'temperature': [float(r['temperature']) for r in records],
        'humidity': [int(r['humidity']) for r in records]
    }
    
    return jsonify(chart_data)
```

---

## Troubleshooting

### Problem: "Storage not initialized"

**Solution:** Call `initialize_storage()` once at application startup:

```python
from data_storage import initialize_storage

# In app.py or main.py
initialize_storage()
```

### Problem: "Permission denied" error

**Solution:** Ensure the `weather_data` directory is writable:

```bash
# On Linux/Mac
chmod 755 weather_data

# On Windows - ensure your user has write permissions
```

### Problem: "No data found"

**Solution:** Verify that data has been saved:

```python
from data_storage import get_storage_stats

stats = get_storage_stats()
print(f"Records in storage: {stats['record_count']}")

# If 0, save some data first
from data_storage import save_weather_data

save_weather_data({
    'city': 'London',
    'temperature': 15.5,
    'humidity': 72,
    'condition': 'Rainy',
    'units': 'metric'
})
```

### Problem: "Invalid weather record" error

**Solution:** Ensure weather data has all required fields:

```python
# ❌ Missing 'condition' field
weather = {
    'city': 'London',
    'temperature': 15.5,
    'humidity': 72
}

# ✅ All required fields present
weather = {
    'city': 'London',
    'temperature': 15.5,
    'humidity': 72,
    'condition': 'Rainy',
    'units': 'metric'
}
```

---

## API Reference

### Functions

#### `initialize_storage()`
Initialize storage directory and create files/tables.

```python
success, message = initialize_storage()
```

#### `save_weather_data(weather_data)`
Save a single weather record.

```python
success, message = save_weather_data({
    'city': 'London',
    'temperature': 15.5,
    'humidity': 72,
    'condition': 'Rainy',
    'units': 'metric'
})
```

#### `save_weather_batch(weather_records)`
Save multiple weather records at once.

```python
success, message = save_weather_batch([
    {'city': 'London', 'temperature': 15.5, 'humidity': 72, 'condition': 'Rainy', 'units': 'metric'},
    {'city': 'Paris', 'temperature': 18.2, 'humidity': 65, 'condition': 'Cloudy', 'units': 'metric'}
])
```

#### `get_weather_data(city=None, limit=100)`
Retrieve weather records.

```python
records = get_weather_data(city='London', limit=50)
```

**Parameters:**
- `city` (str, optional): Filter by city name
- `limit` (int): Maximum records to return (default: 100)

**Returns:** List of weather record dictionaries

#### `get_storage_stats()`
Get statistics about stored data.

```python
stats = get_storage_stats()
# {'storage_type': 'csv', 'storage_dir': 'weather_data', 'record_count': 248, 'file_size_mb': 0.05}
```

#### `export_to_csv_from_sqlite(output_path)`
Export SQLite data to CSV file.

```python
success, message = export_to_csv_from_sqlite('weather_export.csv')
```

---

## Best Practices

1. **Initialize once at startup:** Call `initialize_storage()` in your main Flask app or scheduler startup.

2. **Validate data before saving:** The module validates automatically, but ensure your source data is clean.

3. **Use batching for multiple records:** `save_weather_batch()` is faster than multiple `save_weather_data()` calls.

4. **Set limit when retrieving:** Use `limit` parameter to avoid loading too much data into memory.

5. **Regular backups:** For production, regularly backup your `weather_data` directory.

6. **Monitor storage size:** Check `get_storage_stats()` periodically to track data growth.

---

## Migration Between Storage Types

### From CSV to SQLite

```python
from data_storage import get_weather_data_csv, save_batch_to_sqlite

# Read all CSV data
csv_records = get_weather_data_csv()

# Save to SQLite
success, message = save_batch_to_sqlite(csv_records)
print(message)
```

### From SQLite to CSV

```python
from data_storage import export_to_csv_from_sqlite

success, message = export_to_csv_from_sqlite('weather_backup.csv')
print(message)
```

---

## Performance Tips

| Task | CSV | SQLite |
|------|-----|--------|
| Saving single record | ~1-2ms | ~1-2ms |
| Saving 100 records | ~50-100ms | ~20-50ms |
| Querying 100 records | ~5-10ms | ~1-2ms |
| Querying by city | ~10-50ms | ~1-2ms |
| File size for 1M records | ~200MB | ~100MB |

**Recommendation:** Start with CSV for simplicity, switch to SQLite when you have 10,000+ records or need frequent queries.

---

## Example: Complete Integration

```python
# main.py - Complete example
from flask import Flask
from data_storage import initialize_storage, save_weather_data, get_weather_data
from weather_service import fetch_weather_data

app = Flask(__name__)

@app.before_first_request
def startup():
    """Initialize storage when app starts"""
    initialize_storage()

@app.route('/weather', methods=['GET'])
def get_weather():
    """Fetch weather and save to storage"""
    city = request.args.get('city', 'London')
    
    # Fetch fresh data
    success, weather = fetch_weather_data(city, 'metric')
    
    if success:
        # Save to storage (CSV or SQLite)
        save_weather_data(weather)
        return jsonify(weather)
    
    return jsonify({'error': weather}), 404

@app.route('/weather/history', methods=['GET'])
def get_history():
    """Get historical data from storage"""
    city = request.args.get('city', 'London')
    limit = request.args.get('limit', 100, type=int)
    
    records = get_weather_data(city=city, limit=limit)
    return jsonify({
        'city': city,
        'records': records
    })

if __name__ == '__main__':
    app.run()
```

---

## Next Steps

1. **Choose storage type** in `config.py`
2. **Call `initialize_storage()`** at app startup
3. **Integrate `save_weather_data()`** into your weather collection code
4. **Add `/weather/history` endpoint** to retrieve data for frontend
5. **Display data on dashboard** using the retrieved records

**Questions?** Check the troubleshooting section or review the `data_storage.py` module documentation.
