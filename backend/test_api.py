"""
Test script for Weather API endpoints
Demonstrates how to use single and batch city weather endpoints
"""

import requests
import json

# Base URL - change if running on different host/port
BASE_URL = 'http://localhost:5000'


def test_single_city():
    """Test fetching weather for a single city"""
    print("\n" + "="*60)
    print("TEST 1: Single City Weather")
    print("="*60)
    
    city = 'Hyderabad'
    url = f'{BASE_URL}/weather'
    params = {'city': city, 'units': 'metric'}
    
    print(f"\nRequest: GET {url}?city={city}&units=metric")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_single_city_imperial():
    """Test fetching weather for a single city in Fahrenheit"""
    print("\n" + "="*60)
    print("TEST 2: Single City Weather (Fahrenheit)")
    print("="*60)
    
    city = 'New York'
    url = f'{BASE_URL}/weather'
    params = {'city': city, 'units': 'imperial'}
    
    print(f"\nRequest: GET {url}?city={city}&units=imperial")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_batch_get():
    """Test fetching weather for multiple cities using GET"""
    print("\n" + "="*60)
    print("TEST 3: Batch Weather (GET method)")
    print("="*60)
    
    cities = 'London,Paris,Tokyo'
    url = f'{BASE_URL}/weather/batch'
    params = {'cities': cities, 'units': 'metric'}
    
    print(f"\nRequest: GET {url}?cities={cities}&units=metric")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response:\n{json.dumps(response_data, indent=2)}")
        
        # Check if we got successful results
        if 'successful_count' in response_data:
            print(f"\n✓ Successfully fetched: {response_data['successful_count']} cities")
        if 'failed_count' in response_data and response_data['failed_count'] > 0:
            print(f"✗ Failed to fetch: {response_data['failed_count']} cities")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_batch_post():
    """Test fetching weather for multiple cities using POST"""
    print("\n" + "="*60)
    print("TEST 4: Batch Weather (POST method)")
    print("="*60)
    
    url = f'{BASE_URL}/weather/batch'
    payload = {
        'cities': ['Hyderabad', 'Mumbai', 'Delhi', 'Bangalore'],
        'units': 'metric'
    }
    
    print(f"\nRequest: POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response:\n{json.dumps(response_data, indent=2)}")
        
        # Check if we got successful results
        if 'successful_count' in response_data:
            print(f"\n✓ Successfully fetched: {response_data['successful_count']} cities")
        if 'failed_count' in response_data and response_data['failed_count'] > 0:
            print(f"✗ Failed to fetch: {response_data['failed_count']} cities")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 5: Health Check")
    print("="*60)
    
    url = f'{BASE_URL}/health'
    print(f"\nRequest: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_invalid_city():
    """Test error handling with invalid city"""
    print("\n" + "="*60)
    print("TEST 6: Error Handling (Invalid City)")
    print("="*60)
    
    city = 'InvalidCityXYZ123'
    url = f'{BASE_URL}/weather'
    params = {'city': city}
    
    print(f"\nRequest: GET {url}?city={city}")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code == 404  # Should return 404 for not found
    except Exception as e:
        print(f"Error: {e}")
        return False


def run_all_tests():
    """Run all tests and print summary"""
    print("\n" + "="*60)
    print("Weather Backend API Test Suite")
    print("="*60)
    
    tests = [
        ('Health Check', test_health_check),
        ('Single City', test_single_city),
        ('Single City (Fahrenheit)', test_single_city_imperial),
        ('Batch (GET)', test_batch_get),
        ('Batch (POST)', test_batch_post),
        ('Error Handling', test_invalid_city),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Exception in {test_name}: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Make sure the Flask app is running on localhost:5000")
    print("Start it with: python app.py")
    print("="*60)
    
    success = run_all_tests()
    exit(0 if success else 1)
