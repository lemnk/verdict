#!/usr/bin/env python3
"""
Simple test script for the upload endpoint
Run with: python test_upload.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_upload_endpoint():
    """Test the upload endpoint"""
    print("Testing upload endpoint...")
    
    # Test health check first
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Make sure it's running.")
        return
    
    # Test upload endpoint (this will fail without auth, but shows the endpoint exists)
    try:
        response = requests.post(f"{BASE_URL}/api/upload/")
        print(f"Upload endpoint (no auth): {response.status_code}")
        if response.status_code == 401:
            print("Expected: Authentication required")
    except Exception as e:
        print(f"Error testing upload: {e}")

if __name__ == "__main__":
    test_upload_endpoint()