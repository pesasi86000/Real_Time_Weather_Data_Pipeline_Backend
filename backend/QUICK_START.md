# Quick Start Guide - Weather Dashboard

## Getting Started

### 1. Start the Backend
```bash
cd backend
python app.py
```

You should see:
```
✓ OPENWEATHER_API_KEY is configured
 * Running on http://localhost:5000
```

### 2. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:5000/
```

Or:
```
http://localhost:5000/dashboard-ui
```

### 3. Use the Dashboard
- **Search**: Enter a city name (e.g., "London", "New York", "Tokyo")
- **Units**: Toggle between Celsius and Fahrenheit
- **View**: See real-time weather data and active alerts
- **Refresh**: Click Search again to update data

---

## API Testing

### Test Standard API Endpoint
```bash
curl "http://localhost:5000/weather?city=London&units=metric"
```

### Test Dashboard Endpoint
```bash
curl "http://localhost:5000/dashboard?city=London&units=metric"
```

### Batch Weather Query
```bash
curl -X POST http://localhost:5000/weather/batch \
  -H "Content-Type: application/json" \
  -d '{"cities": ["London", "Paris", "Tokyo"], "units": "metric"}'
```

### Health Check
```bash
curl "http://localhost:5000/health"
```

---

## Response Examples

### Dashboard Response (Success)
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

### With Active Alerts
```json
{
  "success": true,
  "location": { ... },
  "current_weather": { ... },
  "alerts": {
    "active": true,
    "count": 2,
    "items": [
      {
        "type": "HIGH_TEMPERATURE",
        "active": true,
        "message": "High temperature alert: 38°C (threshold: 35°C)",
        "severity": "warning"
      },
      {
        "type": "BAD_WEATHER",
        "active": true,
        "message": "Bad weather alert: Thunderstorm - thunderstorm with light rain",
        "severity": "critical"
      }
    ]
  },
  "timestamp": "2024-04-29T15:30:45Z",
  "units": { ... }
}
```

---

## Available Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/` | GET | Dashboard UI | `http://localhost:5000/` |
| `/dashboard-ui` | GET | Dashboard UI | `http://localhost:5000/dashboard-ui` |
| `/weather` | GET | Weather API | `/weather?city=London&units=metric` |
| `/dashboard` | GET | Dashboard API ⭐ | `/dashboard?city=London&units=metric` |
| `/weather/batch` | POST | Batch Query | Multiple cities in one request |
| `/health` | GET | Health Check | Check backend status |

---

## Features Included

### ✨ Dashboard UI Features
- 🔍 Real-time city search
- 🌡️ Current temperature and "feels like" display
- 💧 Humidity information
- 💨 Wind speed data
- ☁️ Cloud coverage percentage
- 🌍 Location/country info
- ⚠️ Alert notifications with color coding
- 🔄 Unit toggle (Celsius/Fahrenheit)
- 📱 Mobile responsive design
- ⏰ Data fetch timestamp

### 📊 API Features
- Structured JSON responses
- Dashboard-optimized endpoint
- Standard API endpoint
- Batch weather queries
- Comprehensive error handling
- ISO 8601 timestamps
- Unit symbols for display
- Alert severity indicators

### 🚨 Alert System
- **High Temperature**: Triggers at 35°C (95°F)
- **High Humidity**: Triggers at 80% humidity
- **Bad Weather**: Rain, Thunderstorm, Snow, etc.
- **Severity Levels**: Warning (yellow) or Critical (red)
- **Real-time Updates**: Alerts refreshed with each query

---

## Code Structure

```
backend/
├── app.py                    # Flask routes & endpoints
├── weather_service.py        # Weather API integration
├── alerts_service.py         # Alert generation logic
├── response_formatter.py     # ⭐ NEW: Response formatting
├── helpers.py               # Utility functions
├── config.py                # Configuration & settings
├── templates/
│   └── dashboard.html       # ⭐ NEW: Interactive UI
├── API_IMPROVEMENTS.md      # ⭐ NEW: API documentation
└── requirements.txt         # Python dependencies
```

---

## Configuration

Edit `config.py` to adjust:
- Alert temperature thresholds
- Alert humidity threshold
- Bad weather conditions list
- Flask host/port
- Logging settings

---

## Troubleshooting

### Dashboard not loading?
- Check backend is running: `http://localhost:5000/health`
- Verify port 5000 is not in use
- Check browser console for errors (F12)

### API returns 404?
- Verify city name spelling
- Try with country code: "London,GB"
- Check for invalid characters in city name

### No alerts showing?
- Temperature must be ≥ 35°C (95°F)
- Humidity must be ≥ 80%
- Weather must be severe (rain, thunderstorm, etc.)

### Rate limit error?
- Wait a few minutes before making new requests
- Check OpenWeather API rate limits

---

## Documentation

For detailed API documentation, see [API_IMPROVEMENTS.md](./API_IMPROVEMENTS.md)

---

## Support

All responses follow this format:
```json
{
  "success": true/false,
  "data": {...},
  "error": "error_type",
  "message": "error description",
  "timestamp": "ISO 8601 format"
}
```

Check response `error` and `message` fields for troubleshooting.
