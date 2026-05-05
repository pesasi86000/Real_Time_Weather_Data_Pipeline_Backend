# Weather API - Improved Response Structure

## Overview

The Weather Backend has been enhanced with:
- **Structured JSON responses** optimized for both API consumers and dashboard UIs
- **New Dashboard endpoint** with optimized data formatting
- **Comprehensive alerts system** with severity levels
- **Interactive dashboard UI** for real-time weather visualization
- **Improved error handling** with detailed error types and messages

---

## API Endpoints

### 1. `/weather` - Standard API Endpoint

**Purpose**: Fetch weather data with standard API response format

**Method**: `GET`

**Query Parameters**:
- `city` (required): City name (e.g., 'London' or 'London,GB')
- `units` (optional): 'metric' (Celsius) or 'imperial' (Fahrenheit), default: 'metric'

**Example Request**:
```
GET /weather?city=London&units=metric
```

**Response (Success - 200)**:
```json
{
  "success": true,
  "city": "London",
  "country": "GB",
  "current_weather": {
    "temperature": 15,
    "feels_like": 14,
    "humidity": 72,
    "pressure": 1013,
    "condition": "Cloudy",
    "description": "Overcast clouds",
    "wind_speed": 3.5,
    "cloudiness": 90,
    "units": "metric"
  },
  "alerts": {
    "alerts_active": false,
    "alerts": []
  },
  "timestamp": "2024-04-29T15:30:45Z"
}
```

**Response (Error - 404)**:
```json
{
  "success": false,
  "error": "City not found",
  "message": "City 'InvalidCity' not found. Please check the spelling."
}
```

---

### 2. `/dashboard` - Dashboard Optimized Endpoint ⭐ **NEW**

**Purpose**: Fetch weather data specifically optimized for dashboard UI consumption

**Method**: `GET`

**Query Parameters**:
- `city` (required): City name (e.g., 'London' or 'London,GB')
- `units` (optional): 'metric' (Celsius) or 'imperial' (Fahrenheit), default: 'metric'

**Example Request**:
```
GET /dashboard?city=London&units=metric
```

**Response (Success - 200)**:
```json
{
  "success": true,
  "location": {
    "city": "London",
    "country": "GB"
  },
  "current_weather": {
    "temperature": 15,
    "feels_like": 14,
    "condition": "Cloudy",
    "description": "Overcast clouds",
    "humidity": 72,
    "pressure": 1013,
    "wind_speed": 3.5,
    "cloudiness": 90,
    "units": "metric"
  },
  "alerts": {
    "active": false,
    "count": 0,
    "items": []
  },
  "timestamp": "2024-04-29T15:30:45Z",
  "units": {
    "temperature": "°C",
    "wind_speed": "m/s",
    "pressure": "hPa",
    "humidity": "%"
  }
}
```

**Dashboard-Specific Features**:
- Organized location information
- Clear unit symbols for UI display
- Structured alerts with severity levels
- Timestamp in ISO 8601 format
- Count of active alerts
- Perfect for chart/graph visualization

---

### 3. `/dashboard-ui` or `/` - Interactive Dashboard

**Purpose**: Load the interactive weather dashboard UI

**Method**: `GET`

**Example**:
```
GET /
```

**Response**: HTML dashboard page with:
- City search bar
- Unit selector (Celsius/Fahrenheit)
- Real-time weather display
- Alert visualization
- Responsive design (mobile-friendly)

**Access in browser**: `http://localhost:5000/`

---

### 4. `/weather/batch` - Batch Weather Query

**Purpose**: Fetch weather for multiple cities in one request

**Method**: `GET` or `POST`

**GET Parameters**:
- `cities` (required): Comma-separated city names
- `units` (optional): Temperature units

**POST JSON Body**:
```json
{
  "cities": ["London", "Paris", "Tokyo"],
  "units": "metric"
}
```

**Example Requests**:
```bash
# GET request
GET /weather/batch?cities=London,Paris,Tokyo&units=metric

# POST request
POST /weather/batch
Content-Type: application/json

{
  "cities": ["London", "Paris", "Tokyo"],
  "units": "metric"
}
```

**Response**:
```json
{
  "success": true,
  "total_requested": 3,
  "successful": 2,
  "failed": 1,
  "successful_count": 2,
  "failed_count": 1,
  "invalid_format_count": 0,
  "successful": [
    { /* weather data for London */ },
    { /* weather data for Paris */ }
  ],
  "failed": [
    {
      "city": "InvalidCity",
      "error": "City not found"
    }
  ]
}
```

---

### 5. `/health` - Health Check

**Purpose**: Verify backend is running and API key is configured

**Method**: `GET`

**Example**:
```
GET /health
```

**Response**:
```json
{
  "status": "Backend is running",
  "api_key_status": "configured",
  "version": "1.0"
}
```

---

## Alert System

### Alert Types

The system generates alerts for the following conditions:

#### 1. **HIGH_TEMPERATURE** Alert
- **Triggers when**: Temperature exceeds configured threshold
  - Metric: 35°C
  - Imperial: 95°F
- **Severity**: warning
- **Example**:
  ```json
  {
    "type": "HIGH_TEMPERATURE",
    "active": true,
    "message": "High temperature alert: 38°C (threshold: 35°C)",
    "severity": "warning"
  }
  ```

#### 2. **HIGH_HUMIDITY** Alert
- **Triggers when**: Humidity exceeds 80%
- **Severity**: warning
- **Example**:
  ```json
  {
    "type": "HIGH_HUMIDITY",
    "active": true,
    "message": "High humidity alert: 85% (threshold: 80%)",
    "severity": "warning"
  }
  ```

#### 3. **BAD_WEATHER** Alert
- **Triggers when**: Severe weather conditions detected
  - Rain, Thunderstorm, Snow, Fog, Mist, Smoke, Haze, Dust, Ash, Squall, Tornado, Extreme
- **Severity**: 
  - "critical" for: Thunderstorm, Tornado, Hurricane, Extreme
  - "warning" for: Others
- **Example**:
  ```json
  {
    "type": "BAD_WEATHER",
    "active": true,
    "message": "Bad weather alert: Thunderstorm - thunderstorm with light rain",
    "severity": "critical"
  }
  ```

---

## Response Structure Improvements

### Standard API Response Format
```json
{
  "success": true/false,
  "data": {
    // Response-specific data
  },
  "timestamp": "ISO 8601 timestamp",
  "error": "error_type (if applicable)",
  "message": "error_message (if applicable)"
}
```

### Dashboard Response Format
```json
{
  "success": true,
  "location": {
    "city": "string",
    "country": "string"
  },
  "current_weather": {
    "temperature": number,
    "feels_like": number,
    "condition": "string",
    "description": "string",
    "humidity": number (0-100),
    "pressure": number,
    "wind_speed": number,
    "cloudiness": number (0-100),
    "units": "metric|imperial"
  },
  "alerts": {
    "active": boolean,
    "count": number,
    "items": [
      {
        "type": "string",
        "active": boolean,
        "message": "string",
        "severity": "warning|critical"
      }
    ]
  },
  "timestamp": "ISO 8601 timestamp",
  "units": {
    "temperature": "°C|°F",
    "wind_speed": "m/s|mph",
    "pressure": "hPa",
    "humidity": "%"
  }
}
```

---

## HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters or missing required fields |
| 401 | Unauthorized | Invalid API key |
| 404 | Not Found | City not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | External API timeout |

---

## Error Response Examples

### Missing Required Parameter
```json
{
  "success": false,
  "error": "Missing required parameter",
  "message": "The \"city\" parameter is required"
}
```

### Invalid City Format
```json
{
  "success": false,
  "error": "Invalid city format",
  "message": "City name cannot exceed 50 characters"
}
```

### City Not Found
```json
{
  "success": false,
  "error": "City not found",
  "message": "City 'UnknownCity' not found. Please check the spelling."
}
```

### Rate Limit Exceeded
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

---

## Dashboard UI Features

### Main Dashboard Page (`/`)

**Features**:
- 🔍 City search with autocomplete suggestions
- 🌡️ Real-time temperature display
- 📊 Detailed weather metrics (humidity, pressure, wind speed, cloudiness)
- 🌍 Location information (city, country)
- ⚠️ Alert notifications with severity indicators
- 📱 Fully responsive design (mobile, tablet, desktop)
- 🎨 Modern gradient UI with smooth interactions
- ⏰ Data fetch timestamp display

**Supported Features**:
- Search by city name
- Toggle between Celsius and Fahrenheit
- Visual alert indicators
- One-click weather refresh

---

## Timestamps

All API responses include ISO 8601 formatted timestamps:

**Format**: `YYYY-MM-DDTHH:MM:SSZ` (UTC)

**Example**: `2024-04-29T15:30:45Z`

**When Available**:
- `timestamp`: Main response timestamp
- `fetched_at`: When weather data was fetched (included in raw response)

---

## Configuration

All thresholds and settings are configured in `config.py`:

```python
# Alert Thresholds
ALERT_TEMP_HIGH_CELSIUS = 35
ALERT_TEMP_HIGH_FAHRENHEIT = 95
ALERT_HUMIDITY_HIGH = 80
BAD_WEATHER_CONDITIONS = [
    'Rain', 'Thunderstorm', 'Snow', 'Fog', 'Mist', 
    'Smoke', 'Haze', 'Dust', 'Ash', 'Squall', 'Tornado', 'Extreme'
]

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True
```

---

## Code Architecture

### New Files Added

1. **response_formatter.py** - Handles response formatting for different client types
   - `format_weather_for_dashboard()` - Dashboard-optimized format
   - `format_weather_for_api()` - Standard API format
   - `format_batch_response()` - Batch query formatting
   - `get_unit_symbols()` - Unit display symbols

2. **templates/dashboard.html** - Interactive dashboard UI
   - Responsive web interface
   - Real-time weather display
   - Alert visualization

### Updated Files

1. **app.py** - Enhanced with:
   - New `/dashboard` endpoint
   - New `/dashboard-ui` and `/` endpoints for UI
   - Template folder configuration
   - Improved response formatting

2. **weather_service.py** - Added:
   - Timestamp tracking (`fetched_at`)
   - Better structured response data

3. **helpers.py** - No changes (maintains compatibility)

---

## Usage Examples

### JavaScript Fetch
```javascript
// Fetch dashboard data
async function getWeather(city, units = 'metric') {
  const response = await fetch(`/dashboard?city=${city}&units=${units}`);
  const data = await response.json();
  
  if (data.success) {
    console.log(`Temperature: ${data.current_weather.temperature}°C`);
    console.log(`Alerts: ${data.alerts.count}`);
  }
}
```

### Python Requests
```python
import requests

# Fetch weather data
response = requests.get(
    'http://localhost:5000/dashboard',
    params={'city': 'London', 'units': 'metric'}
)
data = response.json()

if data['success']:
    print(f"City: {data['location']['city']}")
    print(f"Temperature: {data['current_weather']['temperature']}")
```

### cURL
```bash
# Get weather data
curl "http://localhost:5000/dashboard?city=London&units=metric"

# Batch query
curl -X POST http://localhost:5000/weather/batch \
  -H "Content-Type: application/json" \
  -d '{"cities": ["London", "Paris", "Tokyo"], "units": "metric"}'
```

---

## Key Improvements Summary

✅ **Structured JSON responses** - Clear organization of weather data  
✅ **Dashboard endpoint** - Optimized for UI consumption  
✅ **Unit symbols** - Display-ready unit information  
✅ **Timestamps** - All responses include ISO 8601 timestamps  
✅ **Alerts system** - Comprehensive weather alerts with severity  
✅ **Interactive UI** - Modern, responsive dashboard  
✅ **Error handling** - Detailed error types and messages  
✅ **Batch operations** - Get weather for multiple cities  
✅ **Mobile-friendly** - Fully responsive design  
✅ **Simple & clean** - Easy to understand and extend  

---

## Next Steps

To test the improvements:

1. **Start the backend**:
   ```bash
   python app.py
   ```

2. **Open the dashboard**:
   - Browser: `http://localhost:5000/`
   - Or: `http://localhost:5000/dashboard-ui`

3. **Test API endpoints**:
   ```bash
   # Standard API
   curl http://localhost:5000/weather?city=London
   
   # Dashboard API
   curl http://localhost:5000/dashboard?city=London
   
   # Batch query
   curl -X POST http://localhost:5000/weather/batch \
     -H "Content-Type: application/json" \
     -d '{"cities": ["London", "Paris"], "units": "metric"}'
   ```

---

## Support

For issues or questions:
- Check the error message in the response
- Verify city name spelling
- Ensure API key is configured
- Check `config.py` for threshold settings
