# Weather Scheduler - Quick Start Guide

## 📋 What You Get

A **scheduled weather data collection system** that automatically fetches weather data every few minutes and saves it to a CSV file. Perfect for building historical weather datasets!

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Verify Your API Key
```bash
# In .env file, make sure you have:
OPENWEATHER_API_KEY=your_actual_key_here
```

### Step 3: Test the Setup
```bash
python test_scheduler.py
```
Choose option 1 to verify everything works.

### Step 4: Run the Scheduler
```bash
python weather_scheduler.py
```

**That's it!** The scheduler will now collect weather data every 5 minutes and save it to `weather_data.csv`.

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `weather_scheduler.py` | **Main scheduler** - Run this for production |
| `weather_scheduler_advanced.py` | Advanced examples for custom schedules |
| `test_scheduler.py` | Testing and verification tool |
| `SCHEDULER_GUIDE.md` | Complete documentation |

---

## 💻 Files in Your Project

```
backend/
├── weather_scheduler.py          ← Run this!
├── weather_scheduler_advanced.py ← Reference for advanced use
├── test_scheduler.py             ← For testing
├── SCHEDULER_GUIDE.md            ← Full documentation
├── weather_data.csv              ← Output file (created automatically)
├── weather_service.py            ← Fetches weather data
├── csv_service.py                ← Saves to CSV
├── fetch_weather_csv.py          ← Batch processing
├── alerts_service.py             ← Alert generation
├── config.py                     ← Configuration
├── helpers.py                    ← Utilities
├── app.py                        ← API endpoints
└── requirements.txt              ← Dependencies
```

---

## ⚙️ Default Configuration

```python
COLLECTION_INTERVAL_MINUTES = 5      # Every 5 minutes
CITIES_TO_MONITOR = [                # 8 major cities
    'London',
    'New York',
    'Tokyo',
    'Paris',
    'Sydney',
    'Dubai',
    'Singapore',
    'Mumbai'
]
TEMPERATURE_UNITS = 'metric'         # Celsius (or 'imperial' for Fahrenheit)
```

---

## 📊 Output: `weather_data.csv`

The scheduler appends data like this:

```
datetime,city,temperature,humidity,condition,units
2026-04-30 14:23:50,London,15.5,72,Rainy,metric
2026-04-30 14:23:52,New York,22.1,65,Clear,metric
2026-04-30 14:28:50,London,15.6,71,Rainy,metric
```

Each line is a new weather observation. Perfect for analysis!

---

## 🎯 Common Tasks

### Change Collection Interval
Edit `weather_scheduler.py` line 30:
```python
COLLECTION_INTERVAL_MINUTES = 10  # Change from 5 to 10
```

### Add or Remove Cities
Edit `weather_scheduler.py` line 20:
```python
CITIES_TO_MONITOR = [
    'New Delhi',
    'Bangkok',
    'Toronto'
]
```

### Use Fahrenheit Instead
Edit `weather_scheduler.py` line 31:
```python
TEMPERATURE_UNITS = 'imperial'
```

### Stop the Scheduler
Press **Ctrl+C** in the terminal.

---

## 🧪 Testing

### Quick Test (Verify configuration)
```bash
python test_scheduler.py
# Choose option 1
```

### Demo Run (60 seconds)
```bash
python test_scheduler.py
# Choose option 2
```

### Check CSV Output
```bash
python test_scheduler.py
# Choose option 4
```

---

## 📜 Understanding the Logs

**Success:**
```
2026-04-30 14:23:45 - fetch_weather_csv - INFO - ✓ Successfully fetched weather for 8 city/cities
```

**Alert (High Temperature):**
```
2026-04-30 14:28:50 - alerts_service - WARNING - London: High temperature alert: 38°C (threshold: 35°C)
```

**Error:**
```
2026-04-30 14:30:00 - fetch_weather_csv - ERROR - ✗ Failed to fetch weather for Tokyo: Invalid API key
```

---

## 🔧 Troubleshooting

**Q: "ModuleNotFoundError: No module named 'schedule'"**  
A: Run `pip install -r requirements.txt`

**Q: "Invalid API key"**  
A: Check your `.env` file has the correct API key from https://openweathermap.org/api

**Q: No CSV file created**  
A: Run `python test_scheduler.py` and check the logs for errors

**Q: How do I run it in the background?**  
A: See "Running in Background" in `SCHEDULER_GUIDE.md`

---

## 🚀 Advanced Usage

See `weather_scheduler_advanced.py` for examples of:
- Different intervals for different city groups
- Scheduling at specific times (e.g., 09:00 daily)
- Retry logic for failed collections
- Loading cities from config files

---

## 📈 What's Happening Behind the Scenes

```
Every 5 minutes:
  1. weather_scheduler.py triggers
  2. Calls fetch_and_save_weather()
  3. For each city:
     a) Fetch from OpenWeather API
     b) Generate alerts (high temp, humidity, bad weather)
     c) Log results
  4. Save all data to weather_data.csv
  5. Log summary
```

---

## 💡 Tips

- **Test first:** Always run `test_scheduler.py` before using in production
- **Start small:** Begin with a few cities and 15-minute intervals
- **Monitor logs:** Watch for errors in the console output
- **Scale gradually:** Add more cities once you're confident
- **Backup data:** Keep backups of `weather_data.csv` as it grows

---

## 🌐 API Rate Limits

Your free OpenWeather tier allows ~60 calls/minute.

**With 8 cities every 5 minutes = ~96 calls/5 min = 19.2 calls/min** ✓ Well within limits!

You can easily:
- Add 30+ cities (20 calls/min)
- Or collect every 1-2 minutes

---

## 📚 Need More Help?

1. **Full documentation:** See `SCHEDULER_GUIDE.md`
2. **Advanced examples:** See `weather_scheduler_advanced.py`
3. **API info:** Run `python app.py` and visit `/dashboard`
4. **Logs:** Check console output for detailed error messages

---

## ✅ Quick Checklist

- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Set API key in `.env`
- [ ] Ran test (`python test_scheduler.py`)
- [ ] Verified CSV output
- [ ] Started scheduler (`python weather_scheduler.py`)
- [ ] Monitored logs for 5 minutes to ensure it's working

**Done!** Your weather scheduler is now collecting data. 🎉

---

## 🎓 Learning Path

1. **Day 1:** Run the basic scheduler, watch it collect data
2. **Day 2:** Try changing the interval and cities
3. **Day 3:** Analyze the CSV data (Excel, Python pandas, etc.)
4. **Day 4:** Try the advanced scheduler examples
5. **Day 5:** Set up in background (Task Scheduler/cron)

---

*Happy weather monitoring! 🌤️*
