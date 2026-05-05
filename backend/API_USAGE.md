# Weather API - Multiple Cities Support

## 📍 Quick Start

Your backend now supports fetching weather data for **single or multiple cities** with simple HTTP requests.

---

## 🔍 API Endpoints

### 1️⃣ Single City Weather
Fetch weather for one city at a time.

**Endpoint:** `GET /weather`

**Parameters:**
- `city` (required): City name (e.g., "Hyderabad", "London,GB")
- `units` (optional): `metric` (Celsius) or `imperial` (Fahrenheit). Default: `metric`

**Example:**
```bash
# Fetch weather for Hyderabad in Celsius
curl "http://localhost:5000/weather?city=Hyderabad"

# Fetch weather for London in Fahrenheit
curl "http://localhost:5000/weather?city=London&units=imperial"
```

**Response (Success - 200):**
```json
{
  "city": "Hyderabad",
  "country": "IN",
  "temperature": 28.5,
  "feels_like": 32.1,
  "humidity": 65,
  "pressure": 1013,
  "condition": "Clouds",
  "description": "overcast clouds",
  "wind_speed": 4.2,
  "cloudiness": 85,
  "units": "metric"
}
```

**Response (Error - 404):**
```json
{
  "error": "Failed to fetch weather",
  "message": "City 'InvalidCityXYZ' not found. Please check the spelling."
}
```

---

### 2️⃣ Multiple Cities Weather (GET)
Fetch weather for multiple cities in a single request using comma-separated names.

**Endpoint:** `GET /weather/batch`

**Parameters:**
- `cities` (required): Comma-separated city names (e.g., "London,Paris,Tokyo")
- `units` (optional): `metric` or `imperial`. Default: `metric`

**Example:**
```bash
# Fetch weather for 3 cities in Celsius
curl "http://localhost:5000/weather/batch?cities=London,Paris,Tokyo"

# Fetch weather for 4 Indian cities in Celsius
curl "http://localhost:5000/weather/batch?cities=Hyderabad,Mumbai,Delhi,Bangalore&units=metric"

# Fetch weather in Fahrenheit
curl "http://localhost:5000/weather/batch?cities=London,New%20York,Tokyo&units=imperial"
```

**Response (Success - 200):**
```json
{
  "successful": [
    {
      "city": "London",
      "country": "GB",
      "temperature": 12.5,
      "humidity": 70,
      "condition": "Rainy",
      "description": "light rain",
      "units": "metric"
    },
    {
      "city": "Paris",
      "country": "FR",
      "temperature": 14.2,
      "humidity": 65,
      "condition": "Cloudy",
      "description": "overcast clouds",
      "units": "metric"
    }
  ],
  "failed": [],
  "total_requested": 2,
  "successful_count": 2,
  "failed_count": 0
}
```

---

### 3️⃣ Multiple Cities Weather (POST)
Fetch weather for multiple cities using JSON request body. Useful for sending large city lists.

**Endpoint:** `POST /weather/batch`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "cities": ["London", "Paris", "Tokyo", "Sydney"],
  "units": "metric"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:5000/weather/batch \
  -H "Content-Type: application/json" \
  -d '{
    "cities": ["Hyderabad", "Mumbai", "Delhi", "Bangalore"],
    "units": "metric"
  }'
```

**Response (Success - 200):**
```json
{
  "successful": [
    {
      "city": "Hyderabad",
      "temperature": 28.5,
      "humidity": 65,
      "condition": "Clouds"
    },
    {
      "city": "Mumbai",
      "temperature": 30.2,
      "humidity": 72,
      "condition": "Partly Cloudy"
    }
  ],
  "failed": [
    {
      "city": "InvalidCity",
      "error": "City 'InvalidCity' not found. Please check the spelling."
    }
  ],
  "total_requested": 3,
  "successful_count": 2,
  "failed_count": 1
}
```

---

### 4️⃣ Health Check
Verify that the backend is running and API key is configured.

**Endpoint:** `GET /health`

**Example:**
```bash
curl "http://localhost:5000/health"
```

**Response:**
```json
{
  "status": "Backend is running",
  "api_key_status": "configured",
  "version": "1.0"
}
```

---

## 🛠️ Python Examples

### Using Python `requests` library

```python
import requests

# Single city
response = requests.get('http://localhost:5000/weather', 
                       params={'city': 'Hyderabad'})
print(response.json())

# Multiple cities (GET)
response = requests.get('http://localhost:5000/weather/batch',
                       params={'cities': 'London,Paris,Tokyo'})
print(response.json())

# Multiple cities (POST)
cities_list = ['London', 'Paris', 'Tokyo', 'Sydney']
response = requests.post('http://localhost:5000/weather/batch',
                        json={'cities': cities_list, 'units': 'metric'})
print(response.json())
```

### Using Python script

Run the test script:
```bash
python test_api.py
```

---

## 📊 Response Fields

Each weather object contains:
- `city`: City name
- `country`: Country code (e.g., "IN", "GB")
- `temperature`: Temperature value
- `feels_like`: "Feels like" temperature
- `humidity`: Humidity percentage (0-100)
- `pressure`: Atmospheric pressure (hPa)
- `condition`: Main weather condition (e.g., "Clouds", "Rain", "Clear")
- `description`: Weather description (e.g., "overcast clouds")
- `wind_speed`: Wind speed
- `cloudiness`: Cloud coverage percentage
- `units`: Temperature units used (metric/imperial)

---

## ⚠️ Error Handling

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Weather data returned |
| 400 | Bad Request | Missing required parameter, invalid units |
| 401 | Unauthorized | API key not configured |
| 404 | Not Found | City doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Unexpected error |

### Error Response Format
```json
{
  "error": "Failed to fetch weather",
  "message": "City 'InvalidCity' not found. Please check the spelling."
}
```

---

## 🚀 Advanced Usage

### Batch with Large City Lists (POST recommended)
```python
cities = [
    'London', 'Paris', 'Berlin', 'Madrid', 'Rome',
    'Tokyo', 'Beijing', 'Mumbai', 'Sydney', 'Dubai'
]

response = requests.post(
    'http://localhost:5000/weather/batch',
    json={
        'cities': cities,
        'units': 'metric'
    }
)

result = response.json()
print(f"Successfully fetched: {result['successful_count']} cities")
print(f"Failed: {result['failed_count']} cities")
```

### Filtering Results
```python
response = requests.get(
    'http://localhost:5000/weather/batch',
    params={'cities': 'London,Paris,InvalidCity,Tokyo'}
)

result = response.json()

# Get only successful cities
successful_cities = [city['city'] for city in result['successful']]
print(f"Successful: {successful_cities}")

# Get only failed cities
failed_cities = [city['city'] for city in result['failed']]
print(f"Failed: {failed_cities}")
```

---

## 📝 Running the Backend

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   # Create .env file or set environment variable
   OPENWEATHER_API_KEY=your_api_key_here
   ```

3. **Run the Flask app:**
   ```bash
   python app.py
   ```

4. **Test the API:**
   ```bash
   python test_api.py
   ```

---

## 🔗 Related Files

- [app.py](app.py) - Flask API routes
- [weather_service.py](weather_service.py) - Weather API logic
- [csv_service.py](csv_service.py) - CSV operations
- [test_api.py](test_api.py) - API test script
- [fetch_weather_csv.py](fetch_weather_csv.py) - Batch CSV export script
