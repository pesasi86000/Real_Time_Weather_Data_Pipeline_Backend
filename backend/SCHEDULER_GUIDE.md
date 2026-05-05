# Weather Data Scheduler Guide

## Overview

The **Weather Data Scheduler** (`weather_scheduler.py`) automatically collects weather data for multiple cities at regular intervals and saves it to a CSV file. This is perfect for building a continuous dataset of weather observations.

---

## How It Works

```
Every 5 minutes (configurable):
  1. Fetch weather data for all configured cities
  2. Check for alerts (high temperature, humidity, bad weather)
  3. Save data to CSV file (weather_data.csv)
  4. Log results with timestamps
```

### Key Features
✓ **Simple scheduler** using the `schedule` library (beginner-friendly)  
✓ **Automatic CSV logging** - appends data with timestamp  
✓ **Alert integration** - logs weather alerts as they occur  
✓ **Graceful shutdown** - stops safely with Ctrl+C  
✓ **Detailed logging** - tracks all operations  
✓ **Easy to customize** - adjust interval, cities, or units  
✓ **Runs continuously** - perfect for background data collection  

---

## Setup & Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `Flask` - API framework
- `requests` - HTTP requests
- `python-dotenv` - Environment variables
- `schedule` - Job scheduling (NEW)

### Step 2: Verify API Key Configuration

Make sure your `OPENWEATHER_API_KEY` is set in `.env`:

```bash
# .env file
OPENWEATHER_API_KEY=your_actual_api_key_here
```

If you don't have one:
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to your `.env` file

---

## Running the Scheduler

### Basic Usage

```bash
python weather_scheduler.py
```

**Output:**
```
2026-04-30 14:23:45 - __main__ - INFO - ======================================================================
2026-04-30 14:23:45 - __main__ - INFO - WEATHER DATA SCHEDULER STARTED
2026-04-30 14:23:45 - __main__ - INFO - ======================================================================
2026-04-30 14:23:45 - __main__ - INFO - Collection interval: Every 5 minute(s)
2026-04-30 14:23:45 - __main__ - INFO - Cities to monitor: London, New York, Tokyo, Paris, Sydney, Dubai, Singapore, Mumbai
2026-04-30 14:23:45 - __main__ - INFO - Temperature units: metric
2026-04-30 14:23:45 - __main__ - INFO - Running initial weather collection...
2026-04-30 14:23:47 - fetch_weather_csv - INFO - Starting weather fetch for 8 city/cities...
2026-04-30 14:23:50 - fetch_weather_csv - INFO - ✓ Fetched weather for London
2026-04-30 14:23:52 - fetch_weather_csv - INFO - ✓ Fetched weather for New York
...
```

### Stop the Scheduler

Press **Ctrl+C** to stop gracefully:

```
^C
2026-04-30 14:28:45 - __main__ - INFO - WEATHER DATA SCHEDULER STOPPED
```

---

## Customization

### Change Collection Interval

Edit `weather_scheduler.py`:

```python
# Line ~24: Change from 5 minutes to your desired interval
COLLECTION_INTERVAL_MINUTES = 5  # Change this number

# Examples:
COLLECTION_INTERVAL_MINUTES = 1   # Every 1 minute
COLLECTION_INTERVAL_MINUTES = 10  # Every 10 minutes
COLLECTION_INTERVAL_MINUTES = 60  # Every 1 hour
```

### Change Cities to Monitor

Edit `weather_scheduler.py`:

```python
# Line ~20: Modify the cities list
CITIES_TO_MONITOR = [
    'London',
    'New York',
    'Tokyo',
    'Paris',
    'Sydney',
    'Dubai',
    'Singapore',
    'Mumbai'
]

# Your custom cities:
CITIES_TO_MONITOR = [
    'New Delhi',
    'Bangkok',
    'Hong Kong',
    'Istanbul'
]
```

### Change Temperature Units

```python
# Line ~31: Change from 'metric' to 'imperial'
TEMPERATURE_UNITS = 'metric'   # Celsius

# Options:
TEMPERATURE_UNITS = 'metric'   # Celsius (°C)
TEMPERATURE_UNITS = 'imperial' # Fahrenheit (°F)
```

### Disable Initial Run

If you don't want the scheduler to run immediately on startup:

```python
# In the start_scheduler() function, comment out this line:
# collect_weather_data()  # Remove this to skip initial run
```

---

## Understanding the Output Files

### CSV Output: `weather_data.csv`

The scheduler appends weather data to this file:

```
datetime,city,temperature,humidity,condition,units
2026-04-30 14:23:50,London,15.5,72,Rainy,metric
2026-04-30 14:23:52,New York,22.1,65,Clear,metric
2026-04-30 14:23:54,Tokyo,18.3,80,Cloudy,metric
2026-04-30 14:28:50,London,15.6,71,Rainy,metric
2026-04-30 14:28:52,New York,22.2,65,Clear,metric
```

**Columns:**
- `datetime` - When the data was collected (YYYY-MM-DD HH:MM:SS)
- `city` - City name
- `temperature` - Current temperature
- `humidity` - Humidity percentage
- `condition` - Weather condition (Clear, Rainy, Cloudy, etc.)
- `units` - Temperature unit (metric or imperial)

### Log Output

Logs are printed to console showing:
- Collection start/end times
- Success/failure for each city
- Any alerts triggered (high temperature, humidity, bad weather)
- Errors with timestamps

Example alert log:
```
2026-04-30 14:28:50 - alerts_service - WARNING - London: High temperature alert: 38°C (threshold: 35°C)
```

---

## Example: Running Multiple Instances

You can run multiple scheduler instances with different cities:

**Terminal 1 - Europe & Asia:**
```bash
# Edit weather_scheduler.py: CITIES_TO_MONITOR = ['London', 'Paris', 'Tokyo', 'Singapore']
python weather_scheduler.py
```

**Terminal 2 - Americas & Oceania:**
```bash
# Edit weather_scheduler.py: CITIES_TO_MONITOR = ['New York', 'Toronto', 'Sydney', 'Buenos Aires']
python weather_scheduler.py
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'schedule'"

**Solution:** Install the schedule library:
```bash
pip install schedule==1.2.0
```

Or update all requirements:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: "Invalid API key"

**Solution:** Check your `.env` file:
```bash
# Make sure this is set correctly
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### Issue: Scheduler runs but no CSV is created

**Possible causes:**
1. API key is invalid - check logs
2. No cities configured - check `CITIES_TO_MONITOR`
3. CSV file permissions issue - check folder permissions
4. Network connection issue - check internet connection

**Debug:** Check the log output carefully for error messages.

---

## Running Scheduler in Background

### On Windows (PowerShell)

```powershell
# Start in background
Start-Process python weather_scheduler.py -WindowStyle Minimized

# Or use a task scheduler (see below)
```

### On Linux/Mac

```bash
# Run with nohup to keep running after terminal closes
nohup python weather_scheduler.py > weather_scheduler.log &

# View the background process
jobs

# Stop the background process
kill %1
```

### Windows Task Scheduler (Advanced)

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "Weather Data Scheduler"
4. Trigger: **Daily** at startup
5. Action: Start a program
   - Program: `python.exe`
   - Arguments: `C:\path\to\weather_scheduler.py`
   - Start in: `C:\path\to\backend`
6. Check "Run whether user is logged in or not"
7. Click **Finish**

---

## Architecture Diagram

```
weather_scheduler.py
    ↓
[Every 5 minutes]
    ↓
fetch_weather_csv.fetch_and_save_weather()
    ↓
    ├─→ weather_service.fetch_weather_data()
    │       ↓
    │   [OpenWeather API]
    │
    ├─→ alerts_service.generate_alerts()
    │       ↓
    │   [Check temperature, humidity, conditions]
    │
    └─→ csv_service.save_weather_to_csv()
            ↓
        weather_data.csv
        [Append new rows]
```

---

## Performance Considerations

### Recommended Intervals

| Use Case | Interval | Notes |
|----------|----------|-------|
| Real-time monitoring | 1-2 minutes | More API calls, more data |
| Typical usage | 5-10 minutes | Good balance |
| Long-term trends | 30-60 minutes | Lower cost, less storage |
| Hourly snapshots | 60 minutes | Minimal API usage |

### API Rate Limits

- Free tier: ~60 calls/minute
- With 8 cities every 5 minutes = 96 calls/5 min = 19.2 calls/min ✓

You have plenty of room for more cities or shorter intervals!

---

## Next Steps

1. **Run the scheduler:** `python weather_scheduler.py`
2. **Let it collect data** for several hours or days
3. **Analyze the CSV** to see weather trends
4. **Create visualizations** from the collected data
5. **Build a dashboard** to display collected data
6. **Set up alerts** to notify when thresholds are exceeded

---

## Questions?

Check the log files for details about what's happening. The scheduler is very verbose with logging to help debug issues.

Happy weather monitoring! 🌤️
