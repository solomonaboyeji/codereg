#!/usr/bin/env python3
"""
Test script to verify the Health Calculator API endpoints work correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_mass_conversion():
    """Test the mass conversion endpoint."""
    print("Testing mass conversion endpoint...")
    
    test_cases = [
        {"mass": 100, "unit_from": "g", "unit_to": "kg"},
        {"mass": 1, "unit_from": "kg", "unit_to": "g"},
        {"mass": 16, "unit_from": "oz", "unit_to": "lb"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {test_case}")
        try:
            response = requests.post(
                f"{BASE_URL}/calculate-mass/",
                json=test_case
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

def test_bmi_calculation():
    """Test the BMI calculation endpoint."""
    print("\n\nTesting BMI calculation endpoint...")
    
    test_cases = [
        {"weight": 70, "height": 1.75, "weight_unit": "kg", "height_unit": "m"},
        {"weight": 154, "height": 5.8, "weight_unit": "lb", "height_unit": "ft"},
        {"weight": 68, "height": 70, "weight_unit": "kg", "height_unit": "in"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {test_case}")
        try:
            response = requests.post(
                f"{BASE_URL}/calculate-bmi/",
                json=test_case
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

def test_welcome_endpoint():
    """Test the welcome endpoint."""
    print("\n\nTesting welcome endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Health Calculator API Test Suite")
    print("=" * 50)
    
    # Note: This test script assumes the server is running
    # To run the server: uvicorn main:app --reload
    print("\nNote: This test script assumes the server is running.")
    print("To run the server: uvicorn main:app --reload")
    print("\nYou can test the API manually using curl or Python requests.")
    print("\nExample curl commands are in the README.md file.")