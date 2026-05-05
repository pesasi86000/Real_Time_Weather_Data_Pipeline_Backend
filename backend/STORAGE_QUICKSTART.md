# Quick Start: Historical Weather Data Storage

## 30-Second Setup

### Step 1: Set Storage Type
Edit `config.py`:
```python
STORAGE_TYPE = 'csv'  # or 'sqlite' for better performance
STORAGE_DIR = 'weather_data'  # directory to store data
```

### Step 2: Initialize Storage
In your main app or scheduler:
```python
from data_storage import initialize_storage
initialize_storage()
```

### Step 3: Save Weather Data
After fetching weather:
```python
from data_storage import save_weather_data

success, message = save_weather_data({
    'city': 'London',
    'temperature': 15.5,
    'humidity': 72,
    'condition': 'Rainy',
    'units': 'metric'
})
```

### Step 4: Retrieve Historical Data
```python
from data_storage import get_weather_data

records = get_weather_data(city='London', limit=100)
for record in records:
    print(f"{record['datetime']}: {record['temperature']}°C")
```

---

## Storage Options at a Glance

| Feature | CSV | SQLite |
|---------|-----|--------|
| Setup | Zero config | Zero config |
| Best for | Beginners | Production |
| Query Speed | Slow (large datasets) | Fast |
| File Size | Large | Compact |
| Export | Direct | `export_to_csv_from_sqlite()` |
| View Directly | Excel/Sheets | SQLite Browser tool |

---

## File Structure

```
backend/
├── config.py              ← Update STORAGE_TYPE here
├── data_storage.py        ← NEW: Core storage module
├── STORAGE_GUIDE.md       ← NEW: Full documentation
├── example_storage_integration.py  ← NEW: Code examples
└── weather_data/          ← AUTO-CREATED: Data directory
    ├── weather_data.csv   (if using CSV)
    └── weather_data.db    (if using SQLite)
```

---

## Common Tasks

### Save Single Record
```python
from data_storage import save_weather_data
save_weather_data({'city': 'London', 'temperature': 15.5, 'humidity': 72, 'condition': 'Rainy', 'units': 'metric'})
```

### Save Multiple Records
```python
from data_storage import save_weather_batch
save_weather_batch([weather1, weather2, weather3])
```

### Get Historical Data
```python
from data_storage import get_weather_data
records = get_weather_data(city='London', limit=50)
```

### Check Storage Size
```python
from data_storage import get_storage_stats
stats = get_storage_stats()
print(f"Records: {stats['record_count']}, Size: {stats['file_size_mb']}MB")
```

### Export SQLite to CSV
```python
from data_storage import export_to_csv_from_sqlite
export_to_csv_from_sqlite('backup.csv')
```

---

## Integration Points

### With Weather Scheduler
```python
# In weather_scheduler.py
from data_storage import initialize_storage, save_weather_batch

initialize_storage()
# ... in collection loop:
save_weather_batch(weather_records)
```

### With Flask API
```python
# In app.py
from data_storage import get_weather_data

@app.route('/api/weather/history')
def history():
    records = get_weather_data(limit=100)
    return jsonify(records)
```

---

## Data Schema

| Field | Type | Example |
|-------|------|---------|
| datetime | String | "2025-05-01 14:30:45" |
| city | String | "London" |
| temperature | Float | 15.5 |
| humidity | Integer | 72 |
| condition | String | "Rainy" |
| units | String | "metric" |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Storage not initialized" | Call `initialize_storage()` at startup |
| "No data found" | Save some data first with `save_weather_data()` |
| "Permission denied" | Ensure `weather_data/` directory is writable |
| "Invalid weather record" | Check all required fields are present |

---

## Next Steps

1. ✅ Choose storage type in `config.py`
2. ✅ Call `initialize_storage()` in your app startup
3. ✅ Add `save_weather_data()` to your data collection code
4. ✅ Add Flask endpoint with `get_weather_data()` for frontend
5. ✅ Display historical data in your dashboard

**Full documentation:** See `STORAGE_GUIDE.md`  
**Examples:** See `example_storage_integration.py`
