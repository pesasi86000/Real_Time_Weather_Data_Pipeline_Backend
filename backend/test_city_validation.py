"""
Test suite for city validation improvements
Tests the enhanced city validation functionality with various edge cases
"""

import json
from weather_service import validate_city

def test_valid_cities():
    """Test validation of valid city names"""
    print("\n=== Testing Valid Cities ===")
    valid_cities = [
        "London",
        "New York",
        "Los Angeles",
        "San Francisco",
        "São Paulo",  # Has special character
        "Moscow",
        "Tokyo",
        "Dubai",
        "St. Petersburg",  # With apostrophe
        "Port-au-Prince",  # With hyphen
        "Hong Kong",
        "London,GB",  # With country code
        "Paris,FR"
    ]
    
    for city in valid_cities:
        is_valid, error = validate_city(city)
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"{status}: '{city}' - {error if error else 'Valid'}")
    

def test_invalid_cities():
    """Test validation of invalid city names"""
    print("\n=== Testing Invalid Cities ===")
    invalid_cities = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("L", "Too short (1 char)"),
        ("a", "Too short (1 char)"),
        ("L@nd0n", "Invalid character (@)"),
        ("London!!", "Invalid characters (!!)"),
        ("London#City", "Invalid character (#)"),
        ("-London", "Starts with hyphen"),
        (",London", "Starts with comma"),
        ("London-", "Ends with hyphen"),
        ("London,", "Ends with comma"),
        ("123" * 50, "Too long (over 100 chars)"),
        ("London@Home", "Invalid character (@)"),
        ("City_Name", "Invalid character (_)"),
    ]
    
    for city, description in invalid_cities:
        is_valid, error = validate_city(city)
        status = "✓ PASS" if not is_valid else "✗ FAIL"
        print(f"{status}: '{city[:30]}...' ({description})")
        if is_valid:
            print(f"       ERROR: Should be invalid but passed!")
        else:
            print(f"       Message: {error}")


def test_edge_cases():
    """Test edge cases"""
    print("\n=== Testing Edge Cases ===")
    test_cases = [
        ("a ", "Has trailing space (should be valid after strip)"),
        (" a", "Has leading space (should be valid after strip)"),
        ("  London  ", "Has surrounding spaces (should be valid after strip)"),
        ("New  York", "Has multiple spaces (should be valid)"),
        ("São Paulo", "Has accented character"),
        ("Paris, France", "With comma and space"),
    ]
    
    for city, description in test_cases:
        is_valid, error = validate_city(city)
        status = "✓" if is_valid else "✗"
        print(f"{status}: '{city}' - {description}")


def format_json_response(success, error_type, message, example=None):
    """Format a JSON error response like the API does"""
    response = {
        "success": success,
        "error": error_type,
        "message": message
    }
    if example:
        response["example"] = example
    return response


def test_json_error_responses():
    """Test that error responses are properly formatted"""
    print("\n=== Testing JSON Error Response Format ===")
    
    test_cases = [
        (False, "Invalid city format", 
         "City name contains invalid characters. Only letters, numbers, spaces, hyphens, apostrophes, and commas are allowed",
         "/weather?city=London&units=metric"),
        (False, "City not found",
         "City 'InvalidCity' not found. Please check the spelling.",
         None),
        (False, "Missing required parameter",
         'The "city" parameter is required',
         "/weather?city=London&units=metric"),
    ]
    
    for success, error, message, example in test_cases:
        response = format_json_response(success, error, message, example)
        print(f"\nError: {error}")
        print(json.dumps(response, indent=2))


def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("CITY VALIDATION TEST SUITE")
    print("=" * 60)
    
    test_valid_cities()
    test_invalid_cities()
    test_edge_cases()
    test_json_error_responses()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
