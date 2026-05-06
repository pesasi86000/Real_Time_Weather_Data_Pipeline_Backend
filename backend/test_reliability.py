"""
Validation and Reliability Test Suite
Tests backend reliability improvements including input validation,
error handling, data storage, and resilience patterns
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weather_service import validate_city, validate_units, extract_weather_info
from alerts_service import generate_alerts
from data_storage import validate_weather_record, format_weather_record
from resilience import RateLimiter, CircuitBreaker, RetryPolicy
from helpers import error_response, success_response


class TestInputValidation(unittest.TestCase):
    """Test input validation for all parameters"""
    
    def test_validate_city_valid(self):
        """Test valid city names"""
        valid_cities = ['London', 'New York', 'Paris', 'San Francisco', 'Tokyo,JP']
        for city in valid_cities:
            is_valid, error = validate_city(city)
            self.assertTrue(is_valid, f"Should accept valid city: {city}")
            self.assertIsNone(error)
    
    def test_validate_city_invalid_empty(self):
        """Test that empty city names are rejected"""
        is_valid, error = validate_city('')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn('required', error.lower())
    
    def test_validate_city_invalid_whitespace_only(self):
        """Test that whitespace-only city names are rejected"""
        is_valid, error = validate_city('   ')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_city_invalid_too_short(self):
        """Test that too-short city names are rejected"""
        is_valid, error = validate_city('A')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn('characters', error.lower())
    
    def test_validate_city_invalid_too_long(self):
        """Test that too-long city names are rejected"""
        long_city = 'A' * 101
        is_valid, error = validate_city(long_city)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_city_invalid_characters(self):
        """Test that cities with invalid characters are rejected"""
        invalid_cities = ['London@#$', 'New~York', 'Paris{test}', 'Tokyo[JP]']
        for city in invalid_cities:
            is_valid, error = validate_city(city)
            self.assertFalse(is_valid, f"Should reject city with invalid chars: {city}")
            self.assertIsNotNone(error)
    
    def test_validate_city_invalid_leading_chars(self):
        """Test that cities with invalid leading characters are rejected"""
        is_valid, error = validate_city('-London')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_units_valid(self):
        """Test valid units parameters"""
        valid_units = ['metric', 'imperial']
        for units in valid_units:
            is_valid, error = validate_units(units)
            self.assertTrue(is_valid, f"Should accept valid units: {units}")
            self.assertIsNone(error)
    
    def test_validate_units_invalid(self):
        """Test invalid units parameters"""
        invalid_units = ['kelvin', 'celsius', 'fahrenheit', 'metric ']
        for units in invalid_units:
            is_valid, error = validate_units(units)
            self.assertFalse(is_valid, f"Should reject invalid units: {units}")
            self.assertIsNotNone(error)


class TestAPIErrorHandling(unittest.TestCase):
    """Test API response handling and error scenarios"""
    
    def test_extract_weather_valid_response(self):
        """Test extracting weather from valid API response"""
        valid_response = {
            'name': 'London',
            'sys': {'country': 'GB'},
            'main': {
                'temp': 15.0,
                'feels_like': 14.0,
                'humidity': 72,
                'pressure': 1013
            },
            'weather': [{'main': 'Cloudy', 'description': 'overcast clouds'}],
            'wind': {'speed': 5.2},
            'clouds': {'all': 90}
        }
        
        result = extract_weather_info(valid_response, 'metric')
        self.assertEqual(result['city'], 'London')
        self.assertEqual(result['temperature'], 15.0)
        self.assertEqual(result['humidity'], 72)
        self.assertEqual(result['condition'], 'Cloudy')
    
    def test_extract_weather_missing_temperature(self):
        """Test that missing temperature raises ValueError"""
        invalid_response = {
            'name': 'London',
            'sys': {'country': 'GB'},
            'main': {'humidity': 72},  # Missing temp
            'weather': [{'main': 'Cloudy'}],
            'wind': {},
            'clouds': {}
        }
        
        with self.assertRaises(ValueError) as ctx:
            extract_weather_info(invalid_response, 'metric')
        self.assertIn('temperature', str(ctx.exception).lower())
    
    def test_extract_weather_missing_humidity(self):
        """Test that missing humidity raises ValueError"""
        invalid_response = {
            'name': 'London',
            'sys': {'country': 'GB'},
            'main': {'temp': 15.0},  # Missing humidity
            'weather': [{'main': 'Cloudy'}],
            'wind': {},
            'clouds': {}
        }
        
        with self.assertRaises(ValueError) as ctx:
            extract_weather_info(invalid_response, 'metric')
        self.assertIn('humidity', str(ctx.exception).lower())
    
    def test_extract_weather_invalid_temperature_type(self):
        """Test that non-numeric temperature raises ValueError"""
        invalid_response = {
            'name': 'London',
            'sys': {'country': 'GB'},
            'main': {'temp': 'fifteen', 'humidity': 72},  # Invalid type
            'weather': [{'main': 'Cloudy'}],
            'wind': {},
            'clouds': {}
        }
        
        with self.assertRaises(ValueError):
            extract_weather_info(invalid_response, 'metric')
    
    def test_extract_weather_with_defaults(self):
        """Test that missing optional fields use safe defaults"""
        response_with_minimal_fields = {
            'name': 'London',
            'sys': {},
            'main': {'temp': 15.0, 'humidity': 72},
            'weather': [{}],
            'wind': {},
            'clouds': {}
        }
        
        result = extract_weather_info(response_with_minimal_fields, 'metric')
        self.assertEqual(result['city'], 'London')
        self.assertEqual(result['country'], 'Unknown')
        self.assertEqual(result['condition'], 'Unknown')
        self.assertEqual(result['description'], 'N/A')
        self.assertEqual(result['wind_speed'], 0)


class TestAlertGeneration(unittest.TestCase):
    """Test alert generation with various weather data scenarios"""
    
    def test_generate_alerts_valid_data(self):
        """Test alert generation with complete valid weather data"""
        weather_data = {
            'temperature': 20,
            'humidity': 60,
            'condition': 'Cloudy',
            'description': 'overcast clouds',
            'units': 'metric',
            'wind_speed': 5,
            'city': 'London'
        }
        
        result = generate_alerts(weather_data)
        self.assertIsInstance(result, dict)
        self.assertIn('alerts_active', result)
        self.assertIn('alerts', result)
        self.assertIsInstance(result['alerts'], list)
    
    def test_generate_alerts_high_temperature(self):
        """Test alert generation for high temperature"""
        weather_data = {
            'temperature': 40,  # High temperature
            'humidity': 60,
            'condition': 'Sunny',
            'description': 'sunny',
            'units': 'metric',
            'wind_speed': 5,
            'city': 'Phoenix'
        }
        
        result = generate_alerts(weather_data)
        self.assertTrue(result['alerts_active'])
        self.assertTrue(len(result['alerts']) > 0)
        alert_types = [a['type'] for a in result['alerts']]
        self.assertIn('HIGH_TEMPERATURE', alert_types)
    
    def test_generate_alerts_high_humidity(self):
        """Test alert generation for high humidity"""
        weather_data = {
            'temperature': 25,
            'humidity': 85,  # High humidity
            'condition': 'Rainy',
            'description': 'light rain',
            'units': 'metric',
            'wind_speed': 5,
            'city': 'Miami'
        }
        
        result = generate_alerts(weather_data)
        self.assertTrue(result['alerts_active'])
        alert_types = [a['type'] for a in result['alerts']]
        self.assertIn('HIGH_HUMIDITY', alert_types)
    
    def test_generate_alerts_bad_weather(self):
        """Test alert generation for bad weather conditions"""
        weather_data = {
            'temperature': 15,
            'humidity': 70,
            'condition': 'Thunderstorm',
            'description': 'severe thunderstorm',
            'units': 'metric',
            'wind_speed': 5,
            'city': 'Kansas'
        }
        
        result = generate_alerts(weather_data)
        self.assertTrue(result['alerts_active'])
        alert_types = [a['type'] for a in result['alerts']]
        self.assertIn('BAD_WEATHER', alert_types)
    
    def test_generate_alerts_missing_required_field(self):
        """Test that missing required fields are handled gracefully"""
        weather_data = {
            'temperature': 20,
            # Missing humidity
            'condition': 'Cloudy',
            'description': 'overcast',
            'units': 'metric',
            'city': 'London'
        }
        
        with self.assertRaises(ValueError):
            generate_alerts(weather_data)
    
    def test_generate_alerts_no_alerts(self):
        """Test that normal conditions produce no alerts"""
        weather_data = {
            'temperature': 20,
            'humidity': 50,
            'condition': 'Partly Cloudy',
            'description': 'partly cloudy',
            'units': 'metric',
            'wind_speed': 2,
            'city': 'London'
        }
        
        result = generate_alerts(weather_data)
        self.assertFalse(result['alerts_active'])
        self.assertEqual(len(result['alerts']), 0)


class TestDataStorageValidation(unittest.TestCase):
    """Test weather record validation for data storage"""
    
    def test_validate_weather_record_valid(self):
        """Test validation of valid weather record"""
        valid_record = {
            'city': 'London',
            'temperature': 15.5,
            'humidity': 72,
            'condition': 'Cloudy'
        }
        
        is_valid, error = validate_weather_record(valid_record)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_weather_record_missing_field(self):
        """Test that missing required fields are caught"""
        invalid_record = {
            'city': 'London',
            'temperature': 15.5
            # Missing humidity and condition
        }
        
        is_valid, error = validate_weather_record(invalid_record)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_weather_record_invalid_temperature(self):
        """Test that non-numeric temperature is rejected"""
        invalid_record = {
            'city': 'London',
            'temperature': 'hot',  # Invalid
            'humidity': 72,
            'condition': 'Cloudy'
        }
        
        is_valid, error = validate_weather_record(invalid_record)
        self.assertFalse(is_valid)
    
    def test_validate_weather_record_invalid_humidity(self):
        """Test that out-of-range humidity is rejected"""
        invalid_record = {
            'city': 'London',
            'temperature': 15.5,
            'humidity': 105,  # Invalid: > 100
            'condition': 'Cloudy'
        }
        
        is_valid, error = validate_weather_record(invalid_record)
        self.assertFalse(is_valid)
        self.assertIn('humidity', error.lower())
    
    def test_format_weather_record(self):
        """Test formatting of weather record for storage"""
        input_record = {
            'city': '  London  ',  # With whitespace
            'temperature': 15.567,  # Multiple decimals
            'humidity': 72,
            'condition': 'Cloudy',
            'units': 'metric'
        }
        
        formatted = format_weather_record(input_record)
        self.assertEqual(formatted['city'], 'London')  # Stripped
        self.assertEqual(formatted['temperature'], 15.57)  # Rounded
        self.assertEqual(formatted['humidity'], 72)


class TestResiencePatterns(unittest.TestCase):
    """Test resilience patterns (rate limiting, circuit breaker)"""
    
    def test_rate_limiter_basic(self):
        """Test basic rate limiter functionality"""
        limiter = RateLimiter(max_requests=3, time_window=10)
        
        # First 3 requests should be allowed
        self.assertTrue(limiter.is_allowed())
        self.assertTrue(limiter.is_allowed())
        self.assertTrue(limiter.is_allowed())
        
        # 4th request should be blocked
        self.assertFalse(limiter.is_allowed())
    
    def test_rate_limiter_retry_after(self):
        """Test rate limiter retry-after calculation"""
        limiter = RateLimiter(max_requests=1, time_window=60)
        
        limiter.is_allowed()  # Use up the request
        retry_after = limiter.get_retry_after()
        
        self.assertGreater(retry_after, 0)
        self.assertLessEqual(retry_after, 60)
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in CLOSED state"""
        breaker = CircuitBreaker(failure_threshold=3)
        
        # In CLOSED state, requests should be allowed
        self.assertTrue(breaker.can_attempt())
        
        # Record some successes
        breaker.record_success()
        breaker.record_success()
        self.assertTrue(breaker.can_attempt())
    
    def test_circuit_breaker_open_state(self):
        """Test circuit breaker opens after failures"""
        breaker = CircuitBreaker(failure_threshold=2)
        
        # Record failures
        breaker.record_failure()
        breaker.record_failure()
        
        # Should be OPEN now
        state = breaker.get_state()
        self.assertEqual(state['state'], 'OPEN')
        self.assertFalse(breaker.can_attempt())
    
    def test_retry_policy_backoff(self):
        """Test retry policy exponential backoff"""
        policy = RetryPolicy(max_attempts=3, base_delay=1, backoff_factor=2)
        
        delay_1 = policy.get_retry_delay(0)
        delay_2 = policy.get_retry_delay(1)
        delay_3 = policy.get_retry_delay(2)
        
        self.assertEqual(delay_1, 1)
        self.assertEqual(delay_2, 2)
        self.assertEqual(delay_3, 4)
    
    def test_retry_policy_max_delay(self):
        """Test retry policy respects max delay"""
        policy = RetryPolicy(max_attempts=5, base_delay=1, backoff_factor=2, max_delay=10)
        
        delay_1 = policy.get_retry_delay(0)  # 1s
        delay_2 = policy.get_retry_delay(1)  # 2s
        delay_3 = policy.get_retry_delay(2)  # 4s
        delay_4 = policy.get_retry_delay(3)  # 8s
        delay_5 = policy.get_retry_delay(4)  # Would be 16s, but capped at 10s
        
        self.assertLessEqual(delay_5, 10)


class TestResponseFormatting(unittest.TestCase):
    """Test response formatting helpers"""
    
    def test_error_response(self):
        """Test error response formatting"""
        response, status = error_response(False, 'Test Error', 'This is a test error', 400)
        
        json_data = response.json
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 'Test Error')
        self.assertEqual(json_data['message'], 'This is a test error')
        self.assertEqual(status, 400)
    
    def test_success_response(self):
        """Test success response formatting"""
        data = {'city': 'London', 'temp': 15}
        response, status = success_response(data, 200)
        
        json_data = response.json
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['city'], 'London')
        self.assertEqual(json_data['temp'], 15)
        self.assertEqual(status, 200)


def run_validation_suite():
    """Run all validation tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataStorageValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestResiencePatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseFormatting))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_validation_suite()
    sys.exit(0 if success else 1)
