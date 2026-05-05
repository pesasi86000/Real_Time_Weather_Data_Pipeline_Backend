# Weather Backend - Refactored Structure

## 📁 Project Organization

Your backend is now organized into clean, modular components:

### **weather_service.py** ⛅
- **Purpose**: Single source of truth for weather API calls
- **Main Function**: `fetch_weather_data(city, units='metric')`
- **Returns**: `(success: bool, data: dict or error_message: str)`
- **Handles**: API validation, error handling, data extraction

**Example Usage:**
```python
from weather_service import fetch_weather_data

success, result = fetch_weather_data('London', units='metric')
if success:
    print(result['temperature'])  # Access weather data
else:
    print(result)  # Error message
```

### **csv_service.py** 📊
- **Purpose**: All CSV file operations in one place
- **Key Functions**:
  - `save_weather_to_csv(weather_records)` - Save records to CSV
  - `format_weather_record(weather_data)` - Convert API data to CSV row
  - `get_csv_record_count()` - Count saved records
  - `get_csv_file_path()` - Get full CSV path

**Example Usage:**
```python
from csv_service import save_weather_to_csv

weather_data = [
    {'city': 'London', 'temperature': 15.2, 'humidity': 65, ...}
]
success, message = save_weather_to_csv(weather_data)
```

### **app.py** 🚀
- **Purpose**: Flask API endpoints
- **Routes**:
  - `GET /weather?city=London&units=metric` - Fetch weather for single city
  - `GET /weather/batch?cities=London,Paris,Tokyo&units=metric` - Fetch weather for multiple cities (comma-separated)
  - `POST /weather/batch` - Fetch weather for multiple cities (JSON body)
  - `GET /health` - Health check
- **Now much simpler**: Uses `weather_service` instead of duplicating code

**Single City Example:**
```bash
curl "http://localhost:5000/weather?city=Hyderabad"
```

**Multiple Cities (GET):**
```bash
curl "http://localhost:5000/weather/batch?cities=London,Paris,Tokyo&units=metric"
```

**Multiple Cities (POST):**
```bash
curl -X POST http://localhost:5000/weather/batch \
  -H "Content-Type: application/json" \
  -d '{"cities": ["London", "Paris", "Tokyo"], "units": "metric"}'
```

### **fetch_weather_csv.py** 📥
- **Purpose**: Batch weather fetching script
- **Main Function**: `fetch_and_save_weather(cities, units='metric')`
- **Usage**: Run from command line to fetch weather for multiple cities

**Example:**
```bash
python fetch_weather_csv.py
```

---

## 🎯 Key Improvements

| Before | After |
|--------|-------|
| Weather API logic duplicated in app.py and fetch_weather_csv.py | Single `fetch_weather_data()` function in weather_service.py |
| CSV saving logic mixed with API logic | Separate csv_service.py handles all CSV operations |
| Long, complex app.py with ~250 lines | Simple app.py with only route handlers |
| Error handling scattered | Centralized error handling in each service |
| Hard to test or reuse | Easy to import and test individual functions |

---

## 💡 Usage Examples

### Example 1: Use in Flask app
Already done! See app.py `/weather` route - it's now 2 lines of actual code.

### Example 2: Use in another Python script
```python
from weather_service import fetch_weather_data
from csv_service import save_weather_to_csv

# Fetch weather
success, weather = fetch_weather_data('Paris', 'metric')

if success:
    # Save to CSV
    save_weather_to_csv([weather])
```

### Example 3: Batch fetch multiple cities
```python
from fetch_weather_csv import fetch_and_save_weather

cities = ['London', 'Paris', 'Tokyo', 'Sydney']
success, message = fetch_and_save_weather(cities)
```

---

## 📝 File Structure Summary

```
backend/
├── app.py                  # Flask API (simple & clean)
├── weather_service.py      # Weather API logic (reusable)
├── csv_service.py         # CSV operations (modular)
├── fetch_weather_csv.py   # Batch script (uses both services)
├── requirements.txt       # Dependencies
└── .env                   # Environment variables
```

---

## 🚀 Next Steps (Optional Enhancements)

1. ✅ **Multiple city support** - Batch endpoints added (`/weather/batch`)
2. **Add unit tests** for weather_service.py
3. **Add database support** instead of CSV
4. **Add scheduled tasks** (celery) for automatic weather updates
5. **Add API documentation** (Swagger/OpenAPI)
6. **Add caching** to reduce API calls

---

## ✅ Benefits of This Structure

✨ **Clean**: Each file has one clear responsibility  
🔄 **Reusable**: Import weather_service anywhere  
🧪 **Testable**: Easy to write unit tests  
🛠️ **Maintainable**: Bug fixes only need to change one place  
📚 **Beginner-friendly**: Clear separation of concerns  
⚡ **Efficient**: No code duplication  
