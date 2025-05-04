#!/usr/bin/env python3
import json
import requests
import sys
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("PORKBUN_API_KEY", "")
SECRET_KEY = os.getenv("PORKBUN_SECRET_API_KEY", "")

if not API_KEY or not SECRET_KEY:
    print("Error: API keys not found in .env file")
    print("Make sure PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY are set in your .env file")
    sys.exit(1)

print(f"Using API Key: {API_KEY[:8]}...")
print(f"Secret Key length: {len(SECRET_KEY)} characters")

# Test different endpoints
endpoints = [
    "https://porkbun.com/api/json/v3/ping",
    "https://api-ipv4.porkbun.com/api/json/v3/ping"
]

for endpoint in endpoints:
    print(f"\nTesting endpoint: {endpoint}")
    
    # Try with both key orders (apikey first, secretapikey first)
    data_variants = [
        {"secretapikey": SECRET_KEY, "apikey": API_KEY},
        {"apikey": API_KEY, "secretapikey": SECRET_KEY}
    ]
    
    for i, data in enumerate(data_variants):
        print(f"\nVariant {i+1}: Keys in order: {', '.join(data.keys())}")
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(endpoint, json=data, headers=headers)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

print("\nDone") 